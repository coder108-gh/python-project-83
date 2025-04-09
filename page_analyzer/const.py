class Errors:
    NO_DB_CONNECTION = -1
    URL_EXISTS = -2
    INVALID_URL = -3
    DB_ERROR = -5
    DATA_NOT_FOUND = -7
    RUNTIME_ERROR = -10
    INCORRECT_DECORATOR_USE = -101


class DbConnInfo:
    NEW_CONNECTION = 1
    OLD_CONNECTION = 0
    NO_CONNECTION = -1


class FlashMsg:
    URL_ADDED = 'Страница успешно добавлена'
    URL_EXISTS = 'Страница уже существует'
    INVALID_URL = 'Некорректный URL'
    URL_CHECKED = 'Страница успешно проверена'


class FlashCtg:
    SUCCESS = 'success'
    INFO = 'info'
    DANDER = 'danger'
    ERROR = 'danger'


class HTTPCodes:
    REDIRECT = 302
    NOT_FOUND = 404
    UNPROCESSABLE_ENTITY = 422
    SERVER_ERROR = 500
