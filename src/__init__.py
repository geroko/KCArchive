from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_basicauth import BasicAuth
from flask_migrate import Migrate
from flask_caching import Cache
from flask_session import Session

app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
basic_auth = BasicAuth(app)
migrate = Migrate(app, db)
cache = Cache(app)
Session(app)

from src import models

db.create_all()

from src import routes
