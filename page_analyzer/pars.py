import requests
from bs4 import BeautifulSoup


def get_if_exists(soup: BeautifulSoup, tag_name: str, def_value=''):
    result = soup.select_one(tag_name)
    if result is None:
        return def_value
    return result.text[:255]


def process_html(html_doc: str):
    soup = BeautifulSoup(html_doc, 'html.parser')
    result = {}
    result['h1'] = get_if_exists(soup, 'h1')
    result['title'] = get_if_exists(soup, 'title')
    result['descr'] = ''

    meta_name = soup.find('meta', attrs={'name': "description"})
    if meta_name is not None:
        cont = meta_name.get('content')
        if cont is not None:
            result['descr'] = cont[:255]
    return result


def get_check_data(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        code = r.status_code
    except requests.HTTPError as e:
        code = e.response.status_code
    except Exception as e:
        raise e

    return {'code': code, 'h1': '', 'title': '', 'descr': ''} | \
        process_html(r.text)

