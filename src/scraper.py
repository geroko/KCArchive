import os
import time
from datetime import datetime
import logging

import requests
import dateutil.parser

from archive import app, db, Post, Thread, File

logging.basicConfig(level=logging.INFO, filename='kcarchive.log', format='%(message)s')

def scrape_catalog(url):
	logging.info(f'\nStarted: {datetime.utcnow()}')
	res = requests.get(url, timeout=5)
	time.sleep(1)
	if res.status_code == 200:
		catalog = res.json()
		for thread in catalog:
			try:
				thread_url = f"https://kohlchan.net/int/res/{thread['threadId']}.json"
				scrape_thread(thread_url)

			except Exception as e:
				print(f"Thread failed: {e}\n{thread}")
				continue

	logging.info(f'Finished: {datetime.utcnow()}')
	return

def scrape_thread(url):
	res = requests.get(url, timeout=5)
	time.sleep(1)
	if res.status_code == 200:
		thread = res.json()
		posts = thread['posts']

		# Try to get thread from db, else instantiate new Thread
		thread_orm = Thread.query.get(thread['threadId'])
		if thread_orm == None:
			thread_orm = Thread(thread_num=thread['threadId'])
			db.session.add(thread_orm)

		scrape_post(thread, thread_orm, is_op=True)

		for post in posts:
			try:
				scrape_post(post, thread_orm, is_op=False)

			except Exception as e:
				logging.error(f'Post failed: {e}\n{post}')
				continue

		thread_orm.total_posts = len(thread_orm.posts_contained)
		db.session.commit()

	return

def scrape_post(post_json, thread_orm, is_op=False):
	if is_op == True:  # OP post uses different key for post number
		post_num = post_json['threadId']
	else:
		post_num = post_json['postId']

	if Post.query.get(post_num):
		return

	mod = post_json['signedRole']
	flag = post_json['flag'].split('/')[-1]
	date = dateutil.parser.isoparse(post_json['creation'])
	subject = post_json['subject']
	if subject == None:
		subject = ''
	message = post_json['message']
	ban_message = post_json.get('banMessage', None)
	files = post_json['files']

	post_orm = Post(flag=flag, date=date, post_num=post_num, subject=subject, mod=mod, message=message, is_op=is_op, thread=thread_orm, ban_message=ban_message)
	db.session.add(post_orm)

	for file in files:
		try:
			scrape_file(file, post_orm)

		except Exception as e:
			logging.error(f'File failed: {e}\n{file}')
			continue

	return

def scrape_file(file_json, post_orm):
	orig_name = file_json['originalName']
	size = file_json['size']

	filename = file_json['thumb'].split('/')[-1]
	if filename == 'spoiler.png':  # Generate filename for spoilered thumbs
		filename = 't_' + file_json['path'].split('/')[-1].split('.')[0]

	width, height = file_json['width'], file_json['height']
	if width == None or height == None:  # If no width or height (such as for audio files), set to None
		dimensions = None
	else:
		dimensions = f"{width}x{height}"

	file_orm = File(filename=filename, orig_name=orig_name, size=size, dimensions=dimensions, post=post_orm)
	db.session.add(file_orm)

	if file_orm.check_blacklisted():
		return

	if os.path.isfile(os.path.join(app.config['MEDIA_FOLDER'], filename)):
		return

	if filename == 'genericThumb.png' or filename == 'audioGenericThumb.png':
		file_url = f"https://kohlchan.net/{filename}"
	else:
		file_url = f"https://kohlchan.net/.media/{filename}"

	res = requests.get(file_url, timeout=5)
	time.sleep(1)
	if res.status_code == 200:
		path = os.path.join(app.config['MEDIA_FOLDER'], filename)
		with open(path, 'wb') as f:
			f.write(res.content)

	return

def purge_blacklisted_files():
	with open(app.config['BLACKLIST_FILE'], 'r') as f:
		for line in f:
			for file in os.listdir(app.config['MEDIA_FOLDER']):
				if file == line.strip('\n'):
					os.remove(os.path.join(app.config['MEDIA_FOLDER'], file))
	
if __name__ == '__main__':
	scrape_catalog('https://kohlchan.net/int/catalog.json')