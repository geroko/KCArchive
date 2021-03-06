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
	subject = StringField(validators=[Optional(), Length(min=3, message='Subject field must be 3 or more characters.')])
	message = StringField(validators=[Optional(), Length(min=3, message='Message field must be 3 or more characters.')])
	is_op = BooleanField()
	banned = BooleanField()
	flag = SelectField(choices=[('Show All', 'Show All')] + [f for f in app.config['FLAG_MAP'].items()], validators=[Optional()])
	start_date = DateField(validators=[Optional()])
	end_date = DateField(validators=[Optional()])
	filename = StringField(validators=[Optional()])
	orig_name = StringField(validators=[Optional()])
	order = SelectField(choices=[('desc', 'Date Descending'), ('asc', 'Date Ascending')], validators=[Optional()])


def report_cooldown(form, submit):
	ip = sha256(get_ip_address().encode('utf-8')).hexdigest()
	reports = Report.query.filter(Report.ip == ip, Report.dismissed == False).order_by(Report.date.desc()).limit(4)
	counter = 0
	for report in reports:
		if datetime.utcnow() - report.date < timedelta(minutes=5):
			counter += 1
		if counter > 2:
			raise ValidationError('Wait before submitting more reports')

def check_already_reported(form, post_num):
	report = Report.query.filter(Report.post_reported == post_num.data).first()
	if report:
		raise ValidationError('Post has already been reported')

class ReportForm(FlaskForm):
	post_num = HiddenField(validators=[check_already_reported])
	reason = TextAreaField(validators=[DataRequired(), Length(max=250)])
