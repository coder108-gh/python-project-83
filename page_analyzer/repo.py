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
    def get_urls(self, cursor=None):

        SQL_STR = 'SELECT id, name, created_at FROM urls \
            ORDER BY created_at DESC'
        cursor.execute(SQL_STR, (id,))
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
