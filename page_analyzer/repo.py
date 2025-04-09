from functools import wraps

import psycopg2
from psycopg2.extras import NamedTupleCursor

from .const import DbConnInfo, Errors
from .result import Result


def db_operation(need_commit: bool):  # noqa: C901
    def deco(func: callable):
        @wraps(func)
        def inner(*args, **kwargs):
            self = args[0]

            if not isinstance(self, Repo):
                return Result(False, Errors.INCORRECT_DECORATOR_USE)

            conn_state = self.db_connect()
            if conn_state == DbConnInfo.NO_CONNECTION:
                return Result(False, Errors.NO_DB_CONNECTION)
            
            with self.db_conn.cursor(cursor_factory=NamedTupleCursor) as cur:
                try:
                    result = func(cursor=cur, *args, **kwargs)
                except psycopg2.Error:
                    result = Result(False, Errors.DB_ERROR)
                except Exception:
                    result = Result(False, Errors.RUNTIME_ERROR)

            is_ok = False
            if isinstance(result, Result) and result.is_ok:
                is_ok = True

            if need_commit and is_ok:
                self.commit()
            elif need_commit:
                self.rollback()

            if conn_state == DbConnInfo.NEW_CONNECTION:
                self.close_conn()

            return result

        return inner
    return deco


class Repo:
    def __init__(self, conn_string: str):
        self.conn_string = conn_string
        self.db_conn = None

    def db_connect(self):
        state = DbConnInfo.OLD_CONNECTION
        if self.db_conn is None:
            try:
                self.db_conn = psycopg2.connect(self.conn_string)
                state = DbConnInfo.NEW_CONNECTION
            except psycopg2.Error:
                state = DbConnInfo.NO_CONNECTION
        return state

    def close_conn(self):
        if self.db_conn is not None:
            self.db_conn.close()
            self.db_conn = None

    def commit(self):
        if self.db_conn is not None:
            self.db_conn.commit()

    def rollback(self):
        if self.db_conn is not None:
            self.db_conn.rollback()

    @db_operation(False)
    def is_no_url(self, url: str, cursor=None):
        SQL_STR = "SELECT id FROM urls WHERE name=(%s)"
        cursor.execute(SQL_STR, (url,))
        return Result(True, value=(cursor.fetchone() is None))

    @db_operation(True)
    def add_new_url(self, url: str, cursor=None):
        if self.is_no_url(url).value:
            SQL_STR = 'INSERT INTO urls (name) VALUES (%s) \
                RETURNING id'
            cursor.execute(SQL_STR, (url,))
            rec = cursor.fetchone()

            result = Result(True, value=rec.id)
        else:
            result = Result(False, Errors.URL_EXISTS)

        return result

    @db_operation(False)
    def get_url_by_id(self, id: int, cursor=None):
        SQL_STR = 'SELECT id, name, created_at FROM urls WHERE id = (%s)'
        cursor.execute(SQL_STR, (id,))
        rec = cursor.fetchone()
        if rec is None:
            return Result(False, Errors.DATA_NOT_FOUND)
        return Result(True, value=rec)

    @db_operation(False)
    def get_checks_by_url(self, id: int, cursor=None):
        SQL_STR = '''
            SELECT 
                id,
                status_code,
                h1,
                title,
                description,
                created_at
            FROM
                url_checks
            WHERE
                url_id = (%s)
            ORDER BY
                created_at DESC'''
        cursor.execute(SQL_STR, (id,))
        return Result(True, value=cursor.fetchall())

    @db_operation(False)
    def get_url_info(self, id: int, cursor=None):

        result = self.get_url_by_id(id)
        if not result.is_ok:
            return result

        tmp = {'data': result.value, 'checks': None}
        checks_result = self.get_checks_by_url(id)
        if checks_result.is_ok:
            tmp['checks'] = checks_result.value
        return Result(True, value=tmp)

    @db_operation(False)
    def get_urls(self, cursor=None):

        SQL_STR = '''
            WITH
            last_checks_url AS
            (SELECT
                url_id,
                MAX(created_at) AS created_at
            FROM url_checks
            GROUP BY url_id),

            last_check AS
            (SELECT url_checks.status_code,
                    last_checks_url.url_id,
                    last_checks_url.created_at
            FROM last_checks_url
            INNER JOIN url_checks ON last_checks_url.url_id = url_checks.url_id
            AND last_checks_url.created_at = url_checks.created_at)

            SELECT urls.name AS name,
                urls.id AS id,
                last_check.status_code AS code,
                last_check.created_at AS last_check
            FROM urls
            LEFT JOIN last_check ON urls.id = last_check.url_id
            ORDER BY last_check.created_at DESC NULLS LAST,
                    urls.created_at DESC;
        '''
        cursor.execute(SQL_STR)
        return Result(True, value=cursor.fetchall())

    @db_operation(True)
    def add_url_check(self, check_data, url_id, cursor=None):
        SQL_STR = '''
            INSERT INTO url_checks
                (url_id, status_code, h1, title, description)
                VALUES (%s, %s, %s, %s, %s)
            RETURNING id'''

        cursor.execute(
            SQL_STR,
            (
                url_id,
                check_data['code'],
                check_data['h1'],
                check_data['title'],
                check_data['descr']
            ),
        )
        rec = cursor.fetchone()
        return Result(True, value=rec.id)
