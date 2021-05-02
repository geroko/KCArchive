import os
import shutil

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_basicauth import BasicAuth
from flask_migrate import Migrate
from flask_caching import Cache
from flask_session import Session

app = Flask(__name__, instance_relative_config=True)

basedir = os.path.dirname(app.root_path)

if not os.path.isdir(os.path.join(basedir, 'instance')):
	os.mkdir(os.path.join(basedir, 'instance'))

if not os.path.isfile(os.path.join(basedir, 'instance/config.py')):
	shutil.copyfile(os.path.join(basedir, 'config.py'), os.path.join(basedir, 'instance/config.py'))

app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
basic_auth = BasicAuth(app)
migrate = Migrate(app, db)
cache = Cache(app)
Session(app)

if not os.path.isdir(app.config['MEDIA_FOLDER']):
	os.mkdir(app.config['MEDIA_FOLDER'])

if not os.path.isfile(app.config['BLACKLIST_FILE']):
	open(app.config['BLACKLIST_FILE'], 'w').close()

from src import models

db.create_all()

from src import routes
