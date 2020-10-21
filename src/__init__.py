import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_basicauth import BasicAuth
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_pyfile('../config.py')
db = SQLAlchemy(app)
basic_auth = BasicAuth(app)
migrate = Migrate(app, db)

if not os.path.isdir(app.config['MEDIA_FOLDER']):
	os.mkdir(app.config['MEDIA_FOLDER'])

if not os.path.isfile(app.config['BLACKLIST_FILE']):
	open(app.config['BLACKLIST_FILE'], 'w').close()

from src import routes
