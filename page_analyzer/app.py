import os

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from .const import Errors, FlashCtg, FlashMsg, HTTPCodes
from .pars import get_check_data
from .repo import Repo
from .result import Result
from .tools import normalize_url, validate_url

try:
    from dotenv import load_dotenv

    load_dotenv()
except ModuleNotFoundError:
    pass


app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["DATABASE_URL"] = DATABASE_URL


def process_error(result: Result):
    if result.error_code == Errors.DATA_NOT_FOUND:
        abort(HTTPCodes.NOT_FOUND)
    abort(HTTPCodes.SERVER_ERROR)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/urls/<int:id>")
def url_info(id: int):
    repo = Repo(DATABASE_URL)
    result = repo.get_url_info(id)
    if result.is_ok:
        return render_template(
            "url_info.html", 
            data=result.value["data"],
            tests=result.value["checks"]
        )
    process_error(result)


@app.post("/urls")
def add_new_url():
    data = request.form.to_dict()
    url = normalize_url(data["url"])
    if validate_url(url):
        repo = Repo(DATABASE_URL)
        result = repo.add_new_url(url)

        if result.is_ok:
            flash(FlashMsg.URL_ADDED, FlashCtg.SUCCESS)
            return redirect(url_for("url_info", id=result.value), code=302)
        else:
            process_error(result)
    else:
        flash(FlashMsg.INVALID_URL, FlashCtg.ERROR)

    return render_template(
        "index.html",
        url_value=data["url"],
    ), HTTPCodes.UNPROCESSABLE_ENTITY


@app.get("/urls")
def url_list():
    repo = Repo(DATABASE_URL)
    result = repo.get_urls()

    if result.is_ok:
        return render_template("url_list.html", url_list=result.value)
    process_error(result)


@app.post("/urls/<int:id>/checks")
def make_url_check(id: int):
    repo = Repo(DATABASE_URL)
    result_url = repo.get_url_by_id(id)
    if not result_url.is_ok and result_url.error_code == Errors.DATA_NOT_FOUND:
        abort(HTTPCodes.NOT_FOUND)
    elif not result_url.is_ok:
        process_error(result_url)

    check_data = get_check_data(result_url.value.name)
 
    result = repo.add_url_check(check_data, id)

    if result.is_ok:
        flash(FlashMsg.URL_CHECKED, FlashCtg.SUCCESS)
        return redirect(url_for("url_info", id=id), code=HTTPCodes.REDIRECT)
    process_error(result)


@app.errorhandler(HTTPCodes.NOT_FOUND)
def page_not_found(error):
    return render_template("error.html"), HTTPCodes.NOT_FOUND
