import os

basedir = os.path.dirname(__file__)

# Set DEBUG to false, and change BASIC_AUTH user and pass before deploying
DEBUG = True
BASIC_AUTH_USERNAME = 'admin'
BASIC_AUTH_PASSWORD = 'changeme'

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:pass@localhost/kcarchive'
SECRET_KEY = os.urandom(16)
MEDIA_FOLDER = os.path.join(basedir, 'media')
BLACKLIST_FILE = os.path.join(basedir, 'blacklist.txt')

CACHE_TYPE = 'redis'
SESSION_TYPE = 'redis'

# Posts newer than this will not be saved, in minutes
SCRAPER_DELAY = 0

BANNER = ''

'''
Add posts to about page with syntax:
{
	'subject':'First post',
	'message':'Hello world'
}
'''
ABOUT = []

