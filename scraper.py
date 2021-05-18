import os
import time
from datetime import datetime, timedelta
import logging
import threading

import requests
import dateutil.parser
from tqdm import tqdm
from sqlalchemy.orm import lazyload

from src import app, db
from src.models import Post, Thread, File
from src.utils import format_message

logging.basicConfig(level=logging.WARNING, filename='instance/kcarchive.log', format='%(message)s')

with open(app.config['BLACKLIST_FILE']) as f:
	blacklist = [line.strip('\n') for line in f]

def scrape_catalog(url):
	logging.warning(f'\nStarted: {datetime.utcnow()}')

	try:
		res = requests.get(url, timeout=5, allow_redirects=False)
		time.sleep(1)
		assert res.status_code == 200, f"Catalog response status code: {res.status_code}."
	except Exception as e:
		logging.error(f"{url} {e}")
		return

	catalog = res.json()
	for thread in tqdm(catalog[::-1]): # Reverse direction to scrape oldest threads first
		db.session.rollback()

		# If thread is < SCRAPER_DELAY minutes old, continue
		if datetime.utcnow() - dateutil.parser.isoparse(thread['creation']).replace(tzinfo=None) < timedelta(minutes=app.config['SCRAPER_DELAY']):
			continue

		thread_orm = Thread.get_or_create(thread['threadId'])
		# If number of posts in thread is same as in database, continue
		if thread['postCount'] + 1 == thread_orm.total_posts:
			continue

		thread_url = f"https://kohlchan.net/int/res/{thread['threadId']}.json"
		scrape_thread(thread_url, thread_orm)

	logging.warning(f'Finished: {datetime.utcnow()}')

def scrape_thread(url, thread_orm=None):
	try:
		res = requests.get(url, timeout=5, allow_redirects=False)
		time.sleep(1)
		assert res.status_code == 200, f"Thread response status code: {res.status_code}."
	except Exception as e:
		logging.error(f"{url} {e}")
		return

	thread = res.json()
	if not thread_orm:
		thread_orm = Thread.get_or_create(thread['threadId'])

	posts = [{k:v for k,v in thread.items() if k != 'posts'}] + thread['posts']
	for post in posts:
		scrape_post(post, thread_orm)

	thread_orm.total_posts = len(thread_orm.posts_contained)
	if thread_orm.total_posts == 0:
		db.session.rollback()
	else:
		db.session.commit()

def scrape_post(post_json, thread_orm):
	is_op = False

	date = dateutil.parser.isoparse(post_json['creation']).replace(tzinfo=None)
	# If post is < SCRAPER_DELAY minutes old, return
	if datetime.utcnow() - date < timedelta(minutes=app.config['SCRAPER_DELAY']):
		return

	try:
		post_num = post_json['postId']
	except:
		post_num = post_json['threadId']
		is_op = True

	ban_message = post_json.get('banMessage', None)

	post_orm = Post.query.options(lazyload(Post.files_contained)).get(post_num)
	if post_orm:
		post_orm.ban_message = ban_message
		return

	try:
		flag = post_json['flag'].split('/')[-1]
		if post_json['flag'].split('/')[-2] == 'vsa':
			flag = 'us-' + flag
		flag_name = post_json['flagName']
	except:
		flag = None
		flag_name = None

	mod = post_json['signedRole']
	email = post_json['email']
	subject = post_json['subject']
	message = post_json['message']
	markdown = format_message(message)

	post_orm = Post(post_num=post_num, date=date, flag=flag, flag_name=flag_name,\
		subject=subject, message=message, markdown=markdown, is_op=is_op,\
		email=email, mod=mod, ban_message=ban_message, thread=thread_orm)
	db.session.add(post_orm)

	files = post_json['files']
	for file in files:
		scrape_file(file, post_orm)

def scrape_file(file_json, post_orm):
	orig_name = file_json['originalName']
	size = file_json['size']

	filename = file_json['thumb'].split('/')[-1]
	file_url = f"https://kohlchan.net{file_json['thumb']}"
	if filename == 'spoiler.png':
		# Generate filename for spoilered thumbs. This has issues since not all thumbs begin with 't_'
		filename = 't_' + file_json['path'].split('/')[-1].split('.')[0]
		file_url = f"https://kohlchan.net/.media/{filename}"

	width, height = file_json['width'], file_json['height']
	if width == None or height == None:  # If no width or height (such as for audio files), set to None
		dimensions = None
	else:
		dimensions = f"{width}x{height}"

	file_orm = File(filename=filename, orig_name=orig_name, size=size, dimensions=dimensions, post=post_orm)
	db.session.add(file_orm)

	if filename in blacklist:
		return

	if os.path.isfile(os.path.join(app.config['MEDIA_FOLDER'], filename)):
		return

	time.sleep(1)
	threading.Thread(target=save_file, args=[file_url]).start()

def save_file(file_url):
	try:
		filename = file_url.split('/')[-1]
		res = requests.get(file_url, timeout=5, allow_redirects=False)
		assert res.status_code == 200, f"File response status code: {res.status_code}."
	except Exception as e:
		logging.error(f"{file_url} {e}")
		return

	path = os.path.join(app.config['MEDIA_FOLDER'], filename)
	with open(path, 'wb') as f:
		f.write(res.content)


def purge_blacklisted_files():
	with open(app.config['BLACKLIST_FILE'], 'r') as f:
		for line in f:
			for file in os.listdir(app.config['MEDIA_FOLDER']):
				if file == line.strip('\n'):
					os.remove(os.path.join(app.config['MEDIA_FOLDER'], file))

if __name__ == '__main__':
	try:
		scrape_catalog('https://kohlchan.net/int/catalog.json')
	except Exception:
		logging.exception('Unexpected exception:')
