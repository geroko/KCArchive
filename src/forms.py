from datetime import datetime, timedelta
from hashlib import sha256

from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField, TextAreaField, HiddenField, SelectField
from wtforms.validators import Optional, DataRequired, ValidationError, Length
from wtforms.fields.html5 import DateField

from src import app
from src.models import Post, File, Report
from src.utils import get_ip_address

def prevent_blank_search(form, submit):
	if not form.post_num.data and not form.subject.data and not form.message.data:
		raise ValidationError("Search criteria required")

class SearchForm(FlaskForm):
	post_num = IntegerField(validators=[Optional()])
	subject = StringField(validators=[Optional()])
	message = StringField(validators=[Optional()])
	is_op = BooleanField()
	banned = BooleanField()
	flag = SelectField(choices=[('Show All', 'Show All')] + [f for f in app.config['FLAG_MAP'].items()])
	start_date = DateField(validators=[Optional()])
	end_date = DateField(validators=[Optional()])
	filename = StringField(validators=[Optional()])
	orig_name = StringField(validators=[Optional()])
	submit = SubmitField()

	# Get data from url args if formdata is empty, disable csrf check
	def __init__(self, *args, **kwargs):
		if 'formdata' not in kwargs:
			kwargs['formdata'] = request.args
		if 'csrf_enabled' not in kwargs:
			kwargs['csrf_enabled'] = False
		super(SearchForm, self).__init__(*args, **kwargs)

	def get_results(self):
		posts = Post.query.group_by(Post.post_num).order_by(Post.date.desc())
		if self.post_num.data:
			posts = posts.filter(Post.post_num == self.post_num.data)
		if self.subject.data:
			posts = posts.filter(Post.subject.contains(self.subject.data))
		if self.message.data:
			posts = posts.filter(Post.message.contains(self.message.data))
		if self.flag.data != 'Show All':
			posts = posts.filter(Post.flag == self.flag.data)
		if self.is_op.data == True:
			posts = posts.filter(Post.is_op == True)
		if self.banned.data == True:
			posts = posts.filter(Post.ban_message != None)
		if self.start_date.data:
			posts = posts.filter(Post.date > self.start_date.data)
		if self.end_date.data:
			posts = posts.filter(Post.date < self.end_date.data)
		if self.filename.data:
			posts = posts.join(Post.files_contained).filter(File.filename.contains(self.filename.data))
		if self.orig_name.data:
			posts = posts.join(Post.files_contained).filter(File.orig_name.contains(self.orig_name.data))
		return posts

def report_cooldown(form, submit):
	ip = sha256(get_ip_address().encode('utf-8')).hexdigest()
	reports = Report.query.filter_by(ip=ip, dismissed=0).order_by(Report.date.desc()).limit(4)
	counter = 0
	for report in reports:
		if datetime.utcnow() - report.date < timedelta(minutes=5):
			counter += 1
		if counter > 2:
			raise ValidationError('Wait before submitting more reports')

def check_already_reported(form, submit):
	post = Post.query.get(form.post_num.data)
	report = Report.query.filter_by(post=post, dismissed=0).first()
	if report:
		raise ValidationError('Post has already been reported')


class ReportForm(FlaskForm):
	post_num = HiddenField()
	reason = TextAreaField(validators=[DataRequired(), Length(max=250)])
	submit = SubmitField(validators=[report_cooldown, check_already_reported])
