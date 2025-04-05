from urllib.parse import urlparse

from validators import url as url_validator


def validate_url(url):
    return (len(url) < 256) and bool(url_validator(url))


def normalize_url(url):
    d = urlparse(url)
    return f'{d.scheme}://{d.netloc}'.lower()
