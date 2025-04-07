from functools import wraps

import psycopg2
from psycopg2.extras import NamedTupleCursor

from .const import (
    DATA_NOT_FOUND,
    INCORRECT_DECORATOR_USE,
    NEW_CONNECTION,
    NO_DATABASE_CONNECTION,
    OK,
    OLD_CONNECTION,
    URL_EXISTS,
)

from .pars import get_check_data


def db_operation(need_commit: bool):
    def deco(func: callable):
        @wraps(func)
        def inner(*args, **kwargs):
            self = args[0]

            if not isinstance(self, Repo):
                return {
                    'state': INCORRECT_DECORATOR_USE,
                    'descr': 'Некорректный программный код',
                    'dev': 'при использовании декоратора db_operation, \
                        в функции первый параметр - объект класса Repo'
                }

            conn_state = self.db_connect()
            if conn_state == NO_DATABASE_CONNECTION:
                return {
                    'state': NO_DATABASE_CONNECTION,
                    'descr': 'Невозможно подключиться к СУБД'
                }
            with self.db_conn.cursor(cursor_factory=NamedTupleCursor) as cur:
                result = func(cursor=cur, *args, **kwargs)

            is_ok = False
            if isinstance(result, dict) and result['state'] == OK:
                is_ok = True
            if isinstance(result, bool):
                is_ok = result

            if need_commit and is_ok:
                self.commit()
            elif need_commit:
                self.rollback()

            if conn_state == NEW_CONNECTION:
                self.close_conn()

            return result

        return inner
    return deco


class Repo:
    def __init__(self, conn_string: str):
        self.conn_string = conn_string
        self.db_conn = None

    def db_connect(self):
        state = OLD_CONNECTION
        if self.db_conn is None:
            try:
                self.db_conn = psycopg2.connect(self.conn_string)
                state = NEW_CONNECTION
            except psycopg2.Error:
                state = NO_DATABASE_CONNECTION

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
        result = False

        SQL_STR = "SELECT id FROM urls WHERE name=(%s)"
        cursor.execute(SQL_STR, (url,))
        tmp = cursor.fetchone()
        result = (tmp is None)

        return result

    @db_operation(True)
    def add_new_url(self, url: str, cursor=None):

        if self.is_no_url(url):
            SQL_STR = 'INSERT INTO urls (name) VALUES (%s) \
                RETURNING id'
            cursor.execute(SQL_STR, (url,))
            rec = cursor.fetchone()

            result = {
                'state': OK,
                'descr': 'Страница успешно добавлена',
                'id': rec.id
            }
        else:
            result = {
                'state': URL_EXISTS,
                'descr': 'Страница уже существует'
            }

        return result

    @db_operation(False)
    def get_url_info(self, id: int, cursor=None):

        result = self.get_url_by_id(id)
        if result['state'] == OK:
            result['checks'] = self.get_checks_by_url(id)

        return result

    @db_operation(False)
    def get_url_by_id(self, id: int, cursor=None):
        SQL_STR = 'SELECT id, name, created_at FROM urls WHERE id = (%s)'
        cursor.execute(SQL_STR, (id,))
        rec = cursor.fetchone()

        if rec is not None:
            result = {
                'state': OK,
                'descr': 'ok',
                'data': rec
            }
        else:
            result = {
                'state': DATA_NOT_FOUND,
                'descr': 'Данные не найдены'
            }
        return result

    @db_operation(False)
    def get_checks_by_url(self, id: int, cursor=None):
        SQL_STR = 'SELECT id, status_code, h1,title, description, created_at \
            FROM url_checks WHERE url_id = (%s) ORDER BY created_at DESC'
        cursor.execute(SQL_STR, (id,))
        rec = cursor.fetchall()
        return rec

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
        records = cursor.fetchall()
        if records is not None:
            result = {
                'state': OK,
                'descr': 'ok',
                'data': records
            }
        else:
            result = {
                'state': DATA_NOT_FOUND,
                'descr': 'Данные не найдены'
            }

        return result

    @db_operation(True)
    def make_url_check(self, url_id, cursor=None):
        result_url = self.get_url_by_id(url_id)
        if result_url['state'] != OK:
            return {
                'state': DATA_NOT_FOUND,
                'descr': 'Не найден url'
            }

        url = result_url['data'].name
        check_data = get_check_data(url)
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

        result = {
            'state': OK,
            'descr': 'Проверка выполнена',
            'id': rec.id
        }
        return result
