import os

# Change BASIC_AUTH user and pass before deploying
BASIC_AUTH_USERNAME = 'admin'
BASIC_AUTH_PASSWORD = 'changeme'

# Change user & pass to your postgres login details
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:pass@localhost/kcarchive'

SECRET_KEY = os.urandom(16)
MEDIA_FOLDER = '/var/www/KCArchive/instance/media'
BLACKLIST_FILE = '/var/www/KCArchive/instance/blacklist.txt'

CACHE_TYPE = 'redis'
SESSION_TYPE = 'redis'

# Posts newer than this will not be saved, in minutes
SCRAPER_DELAY = 0

BANNER = ''

ABOUT = [
	{
		'subject':'Example post',
		'message':'Hello world'
	}
]
