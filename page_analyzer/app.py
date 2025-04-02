import os

from flask import (
    Flask,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

from .repo import DATA_NOT_FOUND, OK, Repo

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass


app = Flask(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = DATABASE_URL


def validate(url):
    return None
 # jinja переделать обращения к полям по наймед тайпл
 # валидации 54:15 отдельный модуль...

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls')
def url_list():
    return '<p>list or url</p>'


@app.route('/urls/<int:id>')
def url_info(id: int, data=None):
    repo = Repo(DATABASE_URL)
    result = repo.get_url_by_id(id)
    if result['state'] == OK:
        return f'<p>url with id={result['data'].id}<br> url={result['data'].name}<br> created_at={result['data'].created_at}</p>'
    if result['state'] == DATA_NOT_FOUND:
        return 'data not found'


@app.post('/urls')
def add_new_url():
    data = request.form.to_dict()
    errors = validate(data['url'])
    if errors:
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            url_value=data['url'],
            errors=errors,
            messages=messages,
        ), 442

    repo = Repo(DATABASE_URL)
    result = repo.add_new_url(data['url'])
    # flash('Страница успешно добавлена', 'success')
    if result['state'] == OK:
        return redirect(url_for('url_info', id=result['id']), code=302)

    return f'<p>Error={result['state']}<br>{result['descr']}</p>'


    #insert url in database, get id of url
    #redirect to page with new id


@app.errorhandler(404)
def page_not_found(error):
    return '<p>page not found</p>'
