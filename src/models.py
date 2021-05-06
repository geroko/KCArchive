import os
from datetime import datetime

from sqlalchemy.dialects.postgresql import TSVECTOR

from src import app, db
from src.utils import format_timedelta, format_bytes, format_message, concat_dicts

class Thread(db.Model):
	thread_num = db.Column(db.Integer, primary_key=True)
	posts_contained = db.relationship('Post', backref='thread', cascade='delete')
	total_posts = db.Column(db.Integer)

	@property
	def post_count(self):
		if self.total_posts == 1:
			return '1 Post'
		return f'{self.total_posts} Posts'

	@property
	def op_post(self):
		for post in self.posts_contained:
			if post.is_op:
				return post

	@property
	def title(self):
		op = self.op_post
		if op.subject:
			return op.subject[:50]
		elif op.message:
			return op.message[:50]
		else:
			return op.post_num

	@classmethod
	def get_or_create(cls, id):
		thread = cls.query.get(id)
		if not thread:
			thread = cls(thread_num=id)
			db.session.add(thread)
		return thread


class Post(db.Model):
	post_num = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.DateTime)
	email = db.Column(db.String(255))
	subject = db.Column(db.String(255))
	message = db.Column(db.Text)
	flag = db.Column(db.String(255))
	flag_name = db.Column(db.String(255))
	mod = db.Column(db.String(255), default=None)
	is_op = db.Column(db.Boolean, default=False)
	ban_message = db.Column(db.String(255), default=None)
	parent_thread = db.Column(db.Integer, db.ForeignKey('thread.thread_num'), nullable=False)
	files_contained = db.relationship('File', backref='post', cascade='delete', lazy='subquery')
	reports_submitted = db.relationship('Report', backref='post')
	markdown = db.Column(db.Text)
	tsv_message = db.Column(TSVECTOR)
	tsv_subject = db.Column(TSVECTOR)

	@property
	def formatted_message(self):
		return format_message(self.message)

	@property
	def timedelta(self):
		td = datetime.utcnow() - self.date
		return f'Posted {format_timedelta(td)} ago'

	def get_replies(self, posts):
		replies = []
		for post in posts:
			if f'>>{self.post_num}' in post.message:
				replies.append(post.post_num)
		return replies


class File(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String(255))
	orig_name = db.Column(db.Text)
	size = db.Column(db.Integer)
	dimensions = db.Column(db.String(255))
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
	ip = db.Column(db.String(255), nullable=False)
	date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	reason = db.Column(db.Text, nullable=False)
	token = db.Column(db.String(255), nullable=False)
	dismissed = db.Column(db.Boolean, default=False)
	post_reported = db.Column(db.Integer, db.ForeignKey('post.post_num'))
