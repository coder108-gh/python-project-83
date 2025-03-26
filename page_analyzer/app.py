import os

import psycopg2
from dotenv import load_dotenv
from flask import Flask

app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)

@app.route("/")
def hello_world():
    return '<p>Hello, World!-py-83</p>'






