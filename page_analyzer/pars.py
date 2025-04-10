import requests


def get_check_data(url):
    code = None
    try:
        r = requests.get(url)
        r.raise_for_status()
        code = r.status_code
    except requests.HTTPError as e:
        code = e.response.status_code
    except Exception as e:
        raise e

    return {"h1": "", "title": "", "code": code, "descr": ""}
