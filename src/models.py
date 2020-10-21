import os
import re
from datetime import datetime

import bleach

from src import app, db
from src.utils import format_timedelta, format_bytes

class Thread(db.Model):
	thread_num = db.Column(db.Integer, primary_key=True)
	posts_contained = db.relationship('Post', backref='thread')
	total_posts = db.Column(db.Integer)


class Post(db.Model):
	post_num = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.DateTime)
	subject = db.Column(db.String, default='')
	message = db.Column(db.String)
	flag = db.Column(db.String)
	mod = db.Column(db.String, default=None)
	is_op = db.Column(db.Boolean, default=False)
	ban_message = db.Column(db.String, default=None)
	parent_thread = db.Column(db.Integer, db.ForeignKey('thread.thread_num'), nullable=False)
	files_contained = db.relationship('File', backref='post', cascade='delete')
	reports_submitted = db.relationship('Report', backref='post')

	def format_message(self):
		formatted = re.sub(r'>', r'&gt;', self.message)
		formatted = re.sub(r'<', r'&lt;', formatted)
		formatted = re.sub(r'(&gt;&gt;(\d+))', r'<a href="#\2" class="reply-link">\1</a>', formatted)
		formatted = re.sub(r'^(&gt;.*)$', r'<span class="greentext">\1</span>', formatted, flags=re.MULTILINE)
		formatted = re.sub(r'^(&lt;.*)$', r'<span class="orangetext">\1</span>', formatted, flags=re.MULTILINE)
		formatted = re.sub(r'\[spoiler\](.*)\[/spoiler\]', r'<span class="spoiler">\1</span>', formatted)
		formatted = re.sub(r'\*\*(.*)\*\*', r'<span class="spoiler">\1</span>', formatted)
		formatted = re.sub(r'==(.*)==', r'<span class="redtext">\1</span>', formatted)
		formatted = re.sub(r'\[b\](.*)\[/b\]', r'<b>\1</b>', formatted)
		formatted = re.sub(r'\'\'\'(.*)\'\'\'', r'<b>\1</b>', formatted)
		formatted = re.sub(r'\[i\](.*)\[/i\]', r'<i>\1</i>', formatted)
		formatted = re.sub(r'\[code\](.*)\[/code\]', r'<code>\1</code>', formatted)
		formatted = re.sub(r'\[u\](.*)\[/u\]', r'<u>\1</u>', formatted)
		formatted = re.sub(r'__(.*)__', r'<u>\1</u>', formatted)
		formatted = re.sub(r'\[s\](.*)\[/s\]', r'<s>\1</s>', formatted)
		formatted = re.sub(r'~~(.*)~~', r'<s>\1</s>', formatted)
		formatted = re.sub(r'\n', r'<br>', formatted)

		formatted = bleach.clean(formatted, tags=['br', 'a', 'span', 'b', 'i', 'code', 'u', 's'], attributes=['class', 'id', 'href'])
		formatted = bleach.linkify(formatted)
		return formatted

	def get_timedelta(self):
		td = datetime.utcnow() - self.date
		return f'Posted {format_timedelta(td)} ago'
	
	def get_flag_name(self):
		return app.config['FLAG_MAP'].get(self.flag, 'Not Available')


class File(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String)
	orig_name = db.Column(db.String)
	size = db.Column(db.Integer)
	dimensions = db.Column(db.String)
	parent_post = db.Column(db.Integer, db.ForeignKey('post.post_num'), nullable=False)

	def delete_file(self):
		with open(app.config['BLACKLIST_FILE'], 'a') as f:
			f.write(self.filename + '\n')
		path = os.path.join(app.config['MEDIA_FOLDER'], self.filename)
		os.remove(path)

	def get_cropped_title(self):
		if len(self.orig_name) > 15:
			name, ext = os.path.splitext(self.orig_name)
			return name[:15] + '[...]' + ext
		else:
			return self.orig_name

	def check_blacklisted(self):
		with open(app.config['BLACKLIST_FILE'], 'r') as f:
			for line in f:
				if self.filename == line.strip('\n'):
					return True

	def get_formatted_size(self):
		if str(self.size).endswith(('B', 'KB', 'MB')):
			return self.size
		return format_bytes(self.size)


class Report(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	ip = db.Column(db.String, nullable=False)
	date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	reason = db.Column(db.String, nullable=False)
	token = db.Column(db.String, nullable=False)
	dismissed = db.Column(db.Boolean, default=False)
	post_reported = db.Column(db.Integer, db.ForeignKey('post.post_num'))

if not os.path.isfile(os.path.join(os.path.dirname(app.root_path), 'kcarchive.db')):
	db.create_all()
