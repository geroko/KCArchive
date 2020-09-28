import os
import re
from datetime import datetime, timedelta
from hashlib import sha256

from flask import Flask, render_template, url_for, send_from_directory, flash, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_wtf import FlaskForm
from flask_basicauth import BasicAuth
from flask_migrate import Migrate
from wtforms import StringField, BooleanField, SubmitField, IntegerField, TextAreaField, HiddenField, SelectField
from wtforms.validators import Optional, DataRequired, ValidationError, Length
from wtforms.fields.html5 import DateField
import bleach

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(app.root_path), 'kcarchive.db')}"
app.config['SECRET_KEY'] = os.urandom(16)
app.config['MEDIA_FOLDER'] = os.path.join(os.path.dirname(app.root_path), 'media')
app.config['BLACKLIST_FILE'] = os.path.join(os.path.dirname(app.root_path), 'blacklist.txt')
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'changeme'
db = SQLAlchemy(app)
basic_auth = BasicAuth(app)
migrate = Migrate(app, db)

if not os.path.isdir(app.config['MEDIA_FOLDER']):
	os.mkdir(app.config['MEDIA_FOLDER'])

FLAG_MAP = {
	'us.png':'United States',
	'de.png':'Germany',
	'ru.png':'Russia',
	'pl.png':'Poland',
	'fi.png':'Finland',
	'ru-mow.png':'Moscow',
	'gb.png':'United Kingdom',
	'ua.png':'Ukraine',
	'proxy.png':'Proxy',
	'br.png':'Brazil',
	'au.png':'Australia',
	'se.png':'Sweden',
	'bavaria.png':'Bavaria',
	'br-south.png':'South Brazil',
	'tr.png':'Turkey',
	'nl.png':'Netherlands',
	'texas.png':'Texas',
	'ca.png':'Canada',
	'fr.png':'France',
	'mx.png':'Mexico',
	'it.png':'Italy',
	'ch.png':'Switzerland',
	'in.png':'India',
	'at.png':'Austria',
	'lv.png':'Latvia',
	'il.png':'Israel',
	'hr.png':'Croatia',
	'pt.png':'Portugal',
	'ar.png':'Argentina',
	'onion.png':'Tor',
	'lt.png':'Lithuania',
	'my.png':'Malaysia',
	'kz.png':'Khazakstan',
	'no.png':'Norway',
	'cl.png':'Chile',
	'rs.png':'Serbia',
	'es.png':'Spain',
	'by.png':'Belarus',
	'gr.png':'Greece',
	'ro.png':'Romania',
	'cz.png':'Czech Republic',
	'ee.png':'Estonia',
	'hu.png':'Hungary',
	'quebec.png':'Quebec',
	'si.png':'Slovenia',
	'ie.png':'Ireland',
	'lu.png':'Luxembourg',
	'scotland.png':'Scotland',
	'co.png':'Colombia',
	'nz.png':'New Zeeland',
	'sk.png':'Slovakia',
	've.png':'Venezuela',
	'am.png':'Armenia',
	'dk.png':'Denmark',
	'az.png':'Azerbijan',
	'kr.png':'South Korea',
	'za.png':'South Africa',
	'crimea.png':'Crimea',
	'cr.png':'Costa Rica',
	'hn.png':'Honduras',
	'ir.png':'Iran',
	'be.png':'Belgium',
	'jp.png':'Japan',
	'is.png':'Iceland',
	'ma.png':'Morocco',
	'catalonia.png':'Catalonia',
	'kw.png':'Kuwait',
	'md.png':'Moldova',
	'pe.png':'Peru',
	'id.png':'Indonesia',
	'bg.png':'Bulgaria',
	'ec.png':'Ecuador',
	'uy.png':'Uraguay',
	'kohl.png':'Moderator'
}

FLAG_MAP = {k:v for k, v in sorted(FLAG_MAP.items(), key=lambda label: label[1])}

'''Models'''
class Post(db.Model):
	post_num = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.DateTime)
	subject = db.Column(db.String, default='')
	message = db.Column(db.String)
	flag = db.Column(db.String)
	mod = db.Column(db.String, default=None)
	is_op = db.Column(db.Boolean, default=False)
	parent_thread = db.Column(db.Integer, db.ForeignKey('thread.thread_num'), nullable=False)
	files_contained = db.relationship('File', backref='post', cascade='delete')
	reports_submitted = db.relationship('Report', backref='post')

	def format_message(self):
		formatted = re.sub(r'>', r'&gt;', self.message)
		formatted = re.sub(r'<', r'&lt;', formatted)
		formatted = re.sub(r'(&gt;&gt;(\d+))', r'<a href="#\2" class="reply-link">\1</a>', formatted)
		formatted = re.sub(r'^(&gt;.*)$', r'<span class="greentext">\1</span>', formatted, flags=re.MULTILINE)
		formatted = re.sub(r'^(&lt;.*)$', r'<span class="orangetext">\1</span>', formatted, flags=re.MULTILINE)
		formatted = re.sub(r'\n', r'<br>', formatted)

		formatted = bleach.clean(formatted, tags=['br', 'a', 'span', 'b', 'i'], attributes=['class', 'id', 'href'])
		formatted = bleach.linkify(formatted)
		return formatted

	def get_timedelta(self):
		td = datetime.utcnow() - self.date
		return f'Posted {format_timedelta(td)} ago'
	
	def get_flag_name(self):
		return FLAG_MAP[self.flag]

class Thread(db.Model):
	thread_num = db.Column(db.Integer, primary_key=True)
	posts_contained = db.relationship('Post', backref='thread')
	total_posts = db.Column(db.Integer)

class File(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String)
	orig_name = db.Column(db.String)
	size = db.Column(db.Integer)
	dimensions = db.Column(db.String)
	parent_post = db.Column(db.Integer, db.ForeignKey('post.post_num'), nullable=False)

	def delete_file(self):
		try:
			with open(app.config['BLACKLIST_FILE'], 'a') as f:
				f.write(self.filename + '\n')
			path = os.path.join(app.config['MEDIA_FOLDER'], self.filename)
			os.remove(path)
		except:
			return

	def get_cropped_title(self):
		if len(self.orig_name) > 15:
			name, ext = os.path.splitext(self.orig_name)
			return name[:15] + '[...]' + ext
		else:
			return self.orig_name

	def check_blacklisted(self):
		if not os.path.isfile(app.config['BLACKLIST_FILE']):
			f = open(app.config['BLACKLIST_FILE'], 'a')
			f.close()
		with open(app.config['BLACKLIST_FILE'], 'r') as f:
			for line in f:
				if self.filename == line.strip('\n'):
					return True

class Report(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	ip = db.Column(db.String, nullable=False)
	date = db.Column(db.DateTime, nullable=False)
	reason = db.Column(db.String, nullable=False)
	token = db.Column(db.String, nullable=False)
	dismissed = db.Column(db.Boolean, default=False)
	post_reported = db.Column(db.Integer, db.ForeignKey('post.post_num'))

if not os.path.isfile(os.path.join(os.path.dirname(app.root_path), 'kcarchive.db')):
	db.create_all()

'''Forms'''
def prevent_blank_search(form, submit):
	if not form.post_num.data and not form.subject.data and not form.message.data:
		raise ValidationError("Search criteria required")

class SearchForm(FlaskForm):
	post_num = IntegerField(validators=[Optional()])
	subject = StringField(validators=[Optional()])
	message = StringField(validators=[Optional()])
	is_op = BooleanField()
	flag = SelectField(choices=[('Show All', 'Show All')] + [f for f in FLAG_MAP.items()])
	start_date = DateField(validators=[Optional()])
	end_date = DateField(validators=[Optional()])
	submit = SubmitField()

	# Get data from url args if formdata is empty, disable csrf check
	def __init__(self, *args, **kwargs):
		if 'formdata' not in kwargs:
			kwargs['formdata'] = request.args
		if 'csrf_enabled' not in kwargs:
			kwargs['csrf_enabled'] = False
		super(SearchForm, self).__init__(*args, **kwargs)

	def get_results(self):
		posts = Post.query.order_by(Post.date.desc())
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
		if self.start_date.data:
			posts = posts.filter(Post.date > self.start_date.data)
		if self.end_date.data:
			posts = posts.filter(Post.date < self.end_date.data)
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
	reason = TextAreaField(validators=[DataRequired(), Length(min=4, max=250)])
	submit = SubmitField(validators=[report_cooldown, check_already_reported])

'''Routes'''
@app.route('/media/<filename>')
def get_media(filename):
	return send_from_directory(app.config['MEDIA_FOLDER'], filename, attachment_filename=filename + '.png')

@app.route('/catalog/', defaults={'page_num':1})
@app.route('/catalog/<int:page_num>')
def catalog(page_num):
	posts = Post.query.order_by(Post.date.desc()).filter(Post.is_op == True).paginate(page=page_num, per_page=50, error_out=False)
	return render_template('catalog.html', posts=posts, title=f'Page {page_num}')

@app.route('/thread/<int:thread_num>')
def thread(thread_num):
	thread = Thread.query.get_or_404(thread_num)
	posts = Post.query.filter_by(thread=thread).all()
	return render_template('thread.html', thread=thread, posts=posts, title=f'#{thread.thread_num}')

@app.route('/search')
def search():
	form = SearchForm()
	return render_template('search.html', form=form, title='Search')

@app.route('/search/', defaults={'page_num':1})
@app.route('/search/<int:page_num>/')
def search_results(page_num):
	form = SearchForm()
	if form.validate():
		query = {'post_num':request.args.get('post_num'), 'subject':request.args.get('subject'), 'message':request.args.get('message'), 'is_op':request.args.get('is_op'), 'flag':request.args.get('flag'), 'start_date':request.args.get('start_date'), 'end_date':request.args.get('end_date')}
		posts = form.get_results()
		posts = posts.paginate(page=page_num, per_page=30, error_out=False)

		return render_template('search.html', form=form, posts=posts, title="Search Results", query=query)
	return render_template('search.html', form=form, title="Search")
	

@app.route('/report/<post_num>', methods=['GET', 'POST'])
def report(post_num):
	post = Post.query.get_or_404(post_num)
	form = ReportForm()
	if form.validate_on_submit():
		report = Report.query.filter_by(token=form.csrf_token.data).first()
		if report:
			return redirect(request.referrer)

		ip = sha256(get_ip_address().encode('utf-8')).hexdigest()
		report = Report(ip=ip, date=datetime.utcnow(), reason=form.reason.data, token=form.csrf_token.data, post=post)
		db.session.add(report)
		db.session.commit()
			
		flash(f'Post #{post.post_num} reported')
		return redirect(url_for('thread', thread_num=post.thread.thread_num))
	return render_template('report_form.html', post=post, form=form, title='Report')

@app.route('/stats')
def stats():
	flag_list = Post.query.with_entities(Post.flag, func.count(Post.flag)).group_by(Post.flag).order_by(func.count(Post.flag).desc()).all()
	
	most_posted = File.query.with_entities(File.filename, func.count(File.filename)).group_by(File.filename).order_by(func.count(File.filename).desc()).limit(100)

	return render_template('stats.html', flag_list=flag_list, most_posted=most_posted, title='Stats', FLAG_MAP=FLAG_MAP)

@app.route('/admin', methods=['GET', 'POST'])
@basic_auth.required
def admin():
	session['admin'] = True
	reports = Report.query.filter_by(dismissed=0).order_by(Report.date.desc()).all()
	return render_template('admin.html', reports=reports)

@app.route('/delete_file/<file_id>', methods=['POST'])
@basic_auth.required
def delete_file(file_id):
	file = File.query.get_or_404(file_id)
	reports = Report.query.filter_by(post=file.post).all()
	
	file.delete_file()
	db.session.commit()

	for report in reports:
		report.dismissed = 1
	db.session.commit()
	return redirect(request.referrer)

@app.route('/delete_files/<post_num>', methods=['POST'])
@basic_auth.required
def delete_files(post_num):
	post = Post.query.get_or_404(post_num)
	reports = Report.query.filter_by(post=post).all()
	
	for file in post.files_contained:
		file.delete_file()

	for report in reports:
		report.dismissed = 1
	db.session.commit()
	return redirect(request.referrer)

@app.route('/dismiss_all', methods=['POST'])
@basic_auth.required
def dismiss_all():
	reports = Report.query.filter_by(dismissed=0).all()
	for report in reports:
		report.dismissed = 1
	db.session.commit()
	return redirect(request.referrer)

@app.route('/dismiss/<report_id>', methods=['POST'])
@basic_auth.required
def dismiss(report_id):
	report = Report.query.get_or_404(report_id)
	report.dismissed = 1
	db.session.commit()
	return redirect(request.referrer)

@app.route('/about')
def about():
	return render_template('about.html', title='About')

@app.route('/')
def index():
	return redirect(url_for('catalog'))


'''Utils'''
def get_ip_address():
	if "X-Forwarded-For" in request.headers:
		return request.headers.getlist("X-Forwarded-For")[0].split()[-1]
	return request.environ["REMOTE_ADDR"]

def format_timedelta(td):
	days, remainder = divmod(int(td.total_seconds()), 86400)
	hours, remainder = divmod(remainder, 3600)
	minutes, seconds = divmod(remainder, 60)

	if minutes < 10:
		minutes = f'0{minutes}'
	if seconds < 10:
		seconds = f'0{seconds}'

	if days > 1:
		return f'{days} Days, {hours}:{minutes}:{seconds}'
	if days == 1:
		return f'{days} Day, {hours}:{minutes}:{seconds}'
	if days < 1:
		return f'{hours}:{minutes}:{seconds}'