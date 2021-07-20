from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from envparse import Env

env = Env()
DB_URL = env.str("DB_URL")

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

db = SQLAlchemy(app)
