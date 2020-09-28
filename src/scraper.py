import os
import time
from datetime import datetime
import logging

import requests
from bs4 import BeautifulSoup

from archive import app, db, Post, Thread, File

logging.basicConfig(level=logging.INFO, filename='kcarchive.log', format='%(message)s')

# TODO: Scrape using lynxchan api
def kc_scrape():
	logging.info(f'\nStarted: {datetime.utcnow()}')
	for thread in get_threads():
		try:
			scrape_thread(thread)
		except:
			continue
	logging.info(f'Finished: {datetime.utcnow()}')

def get_threads():
	res = requests.get('https://kohlchan.net/int/catalog.html')
	time.sleep(1)
	if res.ok:
		soup = BeautifulSoup(res.text, 'lxml')
		thread_links = []
		for thread in soup.find_all('a', class_='labelSubject'):
			thread_link = 'https://kohlchan.net' + thread['href']
			thread_links.append(thread_link)
		return thread_links

def scrape_thread(thread_url):
	res = requests.get(thread_url)
	time.sleep(1)
	if res.ok:
		soup = BeautifulSoup(res.text, 'lxml')

		op_post = soup.find('div', class_='innerOP')
		thread = scrape_post(op_post, is_op=True)

		reply_posts = soup.find_all('div', class_='innerPost')
		for post in reply_posts:
			try:
				scrape_post(post, thread=thread)
			except Exception as e:
				logging.error(f'Post failed: {e}')
				continue

		thread.total_posts = len(thread.posts_contained)
		db.session.commit()

def scrape_post(post, thread=None, is_op=False):
	post_num = post.find('a', class_='linkQuote').text
	
	post_orm = Post.query.get(post_num)
	if post_orm and post_orm.is_op:
		return post_orm.thread
	if post_orm:
		return 

	flag = post.find('img', class_='imgFlag')['src'].split('/')[3]
	date = post.find('span', class_='labelCreated').text
	date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
	try:
		subject = post.find('span', class_='labelSubject').text
	except:
		subject = ''
	try:
		mod = post.find('span', class_='labelRole').text
	except:
		mod = None
	message = post.find('div', class_='divMessage').text

	if thread == None:
		thread = Thread(thread_num=post_num)
		db.session.add(thread)

	post_orm = Post(flag=flag, date=date, post_num=post_num, subject=subject, mod=mod, message=message, is_op=is_op, thread=thread)
	db.session.add(post_orm)

	files = post.find_all('figure', class_='uploadCell')
	for file in files:
		try:
			scrape_file(file, post_orm)
		except Exception as e:
			logging.error(f'File failed: {e}')
			continue
	
	return thread

def scrape_file(file, post):
	if file.img['src'].split('/')[1] == 'spoiler.png':
		filename = "t_" + file.find('a', class_='imgLink')['href'].split('/')[2].split('.')[0] # Create link for spoilered thumbs
	else:
		filename = file.img['src'].split('/')[2] # Audio files with generic thumbnail will cause exception
	orig_name = file.find('a', class_='originalNameLink')['title']
	size = file.find('span', class_='sizeLabel').text
	dimensions = file.find('span', class_='dimensionLabel').text
	file = File(filename=filename, orig_name=orig_name, size=size, dimensions=dimensions, post=post)
	db.session.add(file)
	if file.check_blacklisted():
		return
	
	img_link = 'https://kohlchan.net/.media/' + filename
	try:
		res = requests.get(img_link)
		time.sleep(1)
		if res.ok:
			path = os.path.join(app.config['MEDIA_FOLDER'], filename)
			with open(path, 'wb') as f:
				f.write(res.content)
	except:
		logging.error(f'Failed to Download: {img_link}')
		return		
	

def purge_blacklisted_files():
	if not os.path.isfile(app.config['BLACKLIST_FILE']):
		f = open(app.config['BLACKLIST_FILE'], 'a')
		f.close()
	with open(app.config['BLACKLIST_FILE'], 'r') as f:
		for line in f:
			for file in os.listdir(app.config['MEDIA_FOLDER']):
				if file == line.strip('\n'):
					os.remove(os.path.join(app.config['MEDIA_FOLDER'], file))
	
if __name__ == '__main__':
	kc_scrape()