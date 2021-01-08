import os
from datetime import datetime

from src import app, db
from src.utils import format_timedelta, format_bytes, format_message

class Thread(db.Model):
	thread_num = db.Column(db.Integer, primary_key=True)
	posts_contained = db.relationship('Post', backref='thread')
	total_posts = db.Column(db.Integer)

	@property
	def title(self):
		if self.posts_contained[0].subject:
			return self.posts_contained[0].subject[:50]
		else:
			return self.posts_contained[0].message[:50]

	@property
	def post_count(self):
		if self.total_posts == 1:
			return '1 Post'

		return f'{self.total_posts} Posts'


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
	files_contained = db.relationship('File', backref='post', cascade='delete', lazy='subquery')
	reports_submitted = db.relationship('Report', backref='post')
	markdown = db.Column(db.String)

	@property
	def formatted_message(self):
		return format_message(self.message)

	@property
	def timedelta(self):
		td = datetime.utcnow() - self.date
		return f'Posted {format_timedelta(td)} ago'

	@property
	def flag_name(self):
		return app.config['FLAG_MAP'].get(self.flag, 'Not Available')

	def get_replies(self, posts):
		replies = []
		for post in posts:
			if f'>>{self.post_num}' in post.message:
				replies.append(post.post_num)
		return replies


class File(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String)
	orig_name = db.Column(db.String)
	size = db.Column(db.Integer)
	dimensions = db.Column(db.String)
	parent_post = db.Column(db.Integer, db.ForeignKey('post.post_num'), nullable=False)

	def delete_file(self):
		if self.is_blacklisted:
			return

		with open(app.config['BLACKLIST_FILE'], 'a') as f:
			f.write(self.filename + '\n')

		path = os.path.join(app.config['MEDIA_FOLDER'], self.filename)
		if os.path.exists(path):
			os.remove(path)

	@property
	def cropped_title(self):
		if len(self.orig_name) > 15:
			name, ext = os.path.splitext(self.orig_name)
			return name[:15] + '[...]' + ext
		else:
			return self.orig_name

	@property
	def is_blacklisted(self):
		with open(app.config['BLACKLIST_FILE'], 'r') as f:
			if self.filename in [line.strip('\n') for line in f]:
				return True
			return False

	@property
	def formatted_size(self):
		return format_bytes(self.size)


class Report(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	ip = db.Column(db.String, nullable=False)
	date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	reason = db.Column(db.String, nullable=False)
	token = db.Column(db.String, nullable=False)
	dismissed = db.Column(db.Boolean, default=False)
	post_reported = db.Column(db.Integer, db.ForeignKey('post.post_num'))
