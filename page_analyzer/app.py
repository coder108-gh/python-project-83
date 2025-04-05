import os

from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

from .const import DATA_NOT_FOUND, FLASH_CATEGORY, INVALID_URL, OK
from .repo import Repo
from .tools import normalize_url, validate_url

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass


app = Flask(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = DATABASE_URL


# валидации 54:15 отдельный модуль...
# def validate(url):
#     result = True
#     if not validate_url(url):
#     return result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls')
def url_list():

    repo = Repo(DATABASE_URL)
    result = repo.get_urls()
    if result['state'] == OK:
        return render_template("url_list.html", url_list=result['data'])
    if result['state'] == DATA_NOT_FOUND:
        return 'data not found'
    


@app.route('/urls/<int:id>')
def url_info(id: int):
    repo = Repo(DATABASE_URL)
    result = repo.get_url_by_id(id)
    if result['state'] == OK:
        return render_template("url_info.html", data=result['data'])
    if result['state'] == DATA_NOT_FOUND:
        return 'data not found'


@app.post('/urls')
def add_new_url():
    data = request.form.to_dict()
    url = normalize_url(data['url'])
    if validate_url(url):
        repo = Repo(DATABASE_URL)
        result = repo.add_new_url(data['url'])
        if result['state'] == OK:
            flash(result['descr'], FLASH_CATEGORY[OK])
            return redirect(url_for('url_info', id=result['id']), code=302)
        else:
            flash(result['descr'], FLASH_CATEGORY[result['state']])
    else:
        flash('Некорректный URL', FLASH_CATEGORY[INVALID_URL])

    return render_template(
        'index.html',
        url_value=data['url'],
    ), 442


@app.errorhandler(404)
def page_not_found(error):
    return '<p>page not found</p>'
