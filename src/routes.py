from hashlib import sha256
from math import ceil

from flask import render_template, url_for, send_from_directory, flash, redirect, request, session, g
from sqlalchemy import func
from sqlalchemy.orm import lazyload

from src import app, db, basic_auth, cache
from src.models import Thread, Post, File, Report
from src.forms import SearchForm, ReportForm
from src.utils import get_ip_address, referrer_or_index, concat_dicts
from src.search import search_posts

@app.route('/media/<filename>')
def get_media(filename):
	return send_from_directory(app.config['MEDIA_FOLDER'], filename, attachment_filename=filename + '.png')

@app.before_request
def get_banner_message():
	g.banner = app.config['BANNER']

@app.route('/catalog/', defaults={'page_num':1})
@app.route('/catalog/<int:page_num>')
def catalog(page_num):
	threads = Thread.query.order_by(Thread.thread_num.desc()).filter(Thread.total_posts != None).paginate(page=page_num, per_page=50, error_out=False)
	return render_template('catalog.html', threads=threads, title=f'Page {page_num}')

@app.route('/thread/<int:thread_num>')
def thread(thread_num):
	thread = Thread.query.get_or_404(thread_num)
	posts = Post.query.filter(Post.thread == thread).order_by(Post.post_num).all()
	return render_template('thread.html', posts=posts, title=thread.title, post_count=thread.total_posts)

@app.route('/search')
def search():
	form = SearchForm()
	return render_template('search.html', form=form, title='Search')

@app.route('/search/', defaults={'page_num':1})
@app.route('/search/<int:page_num>')
def search_results(page_num):
	form = SearchForm(formdata=request.args, meta={'csrf':False})
	if form.validate():
		results = search_posts(**form.data)
		offset = (page_num - 1) * 30
		if offset > 5000 or offset < 0:
			offset = 0
			page_num = 1
		posts = results.offset(offset).limit(30)
		return render_template('search.html', form=form, posts=posts, title="Search Results", query=request.args, page_num=page_num)
	return render_template('search.html', form=form, title="Search")

@app.route('/report/<int:post_num>', methods=['GET', 'POST'])
def report(post_num):
	post = Post.query.get_or_404(post_num)
	form = ReportForm()
	if form.validate_on_submit():
		ip = sha256(get_ip_address().encode('utf-8')).hexdigest()
		report = Report(ip=ip, reason=form.reason.data, token=form.csrf_token.data, post=post)
		db.session.add(report)
		db.session.commit()

		flash(f'Post #{post.post_num} reported')
		return redirect(url_for('thread', thread_num=post.thread.thread_num))
	return render_template('report_form.html', post=post, form=form, title='Report')

@cache.cached(timeout=86400, key_prefix='stats')
def get_cached_stats():
	flag_list = Post.query.with_entities(Post.flag, Post.flag_name, func.count(Post.flag))\
		.filter(Post.flag != None, Post.flag_name != None)\
		.group_by(Post.flag, Post.flag_name)\
		.order_by(func.count(Post.flag).desc()).all()

	most_posted = File.query.with_entities(File.filename, func.count(File.filename))\
		.filter(File.filename != 'audioGenericThumb.png', File.filename != 'genericThumb.png')\
		.group_by(File.filename)\
		.order_by(func.count(File.filename).desc()).limit(100).all()

	return flag_list, most_posted

@app.route('/stats')
def stats():
	flag_list, most_posted = get_cached_stats()
	return render_template('stats.html', flag_list=flag_list, most_posted=most_posted, title='Stats')

@app.route('/admin', methods=['GET', 'POST'])
@basic_auth.required
def admin():
	session['admin'] = True
	reports = Report.query.filter(Report.dismissed == False).order_by(Report.date.desc()).all()
	return render_template('admin.html', reports=reports)

@app.route('/delete_file/<int:file_id>', methods=['POST'])
@basic_auth.required
def delete_file(file_id):
	file = File.query.get_or_404(file_id)
	report = Report.query.filter(Report.post == file.post, Report.dismissed == False).first()

	file.delete_file()

	if report:
		report.dismissed = True
		db.session.commit()

	flash(f'File: {file.cropped_title} deleted.')
	return redirect(referrer_or_index())

@app.route('/delete_files/<int:post_num>', methods=['POST'])
@basic_auth.required
def delete_files(post_num):
	post = Post.query.get_or_404(post_num)
	report = Report.query.filter(Report.post == post, Report.dismissed == False).first()

	for file in post.files_contained:
		file.delete_file()

	if report:
		report.dismissed = True
		db.session.commit()

	flash(f'Files: {", ".join([file.cropped_title for file in post.files_contained])} deleted.')
	return redirect(referrer_or_index())

@app.route('/dismiss_all', methods=['POST'])
@basic_auth.required
def dismiss_all():
	reports = Report.query.filter(Report.dismissed == False).all()
	for report in reports:
		report.dismissed = True
	db.session.commit()
	return redirect(referrer_or_index())

@app.route('/dismiss/<int:report_id>', methods=['POST'])
@basic_auth.required
def dismiss(report_id):
	report = Report.query.get_or_404(report_id)
	report.dismissed = True
	db.session.commit()
	return redirect(referrer_or_index())

@app.route('/about')
def about():
	return render_template('about.html', title='About', about_content=app.config['ABOUT'])

@app.route('/')
def index():
	return redirect(url_for('catalog'))

@app.route('/change_theme', methods=['POST'])
def change_theme():
	if session.get('theme', None) == 'dark':
		session.pop('theme')
	else:
		session['theme'] = 'dark'
	return redirect(referrer_or_index())
