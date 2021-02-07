from hashlib import sha256

from flask import render_template, url_for, send_from_directory, flash, redirect, request, session
from sqlalchemy import func

from src import app, db, basic_auth
from src.models import Thread, Post, File, Report
from src.forms import SearchForm, ReportForm
from src.utils import get_ip_address, referrer_or_index
from src.search import search_posts

@app.route('/media/<filename>')
def get_media(filename):
	return send_from_directory(app.config['MEDIA_FOLDER'], filename, attachment_filename=filename + '.png')

@app.route('/catalog/', defaults={'page_num':1})
@app.route('/catalog/<int:page_num>')
def catalog(page_num):
	posts = Post.query.order_by(Post.post_num.desc()).filter(Post.is_op == True).paginate(page=page_num, per_page=50, error_out=False)
	return render_template('catalog.html', posts=posts, title=f'Page {page_num}')

@app.route('/thread/<int:thread_num>')
def thread(thread_num):
	thread = Thread.query.get_or_404(thread_num)
	posts = Post.query.filter(Post.thread == thread).all()
	return render_template('thread.html', posts=posts, title=thread.title)

@app.route('/search')
def search():
	form = SearchForm()
	return render_template('search.html', form=form, title='Search')

@app.route('/search/', defaults={'page_num':1})
@app.route('/search/<int:page_num>/')
def search_results(page_num):
	form = SearchForm(formdata=request.args, meta={'csrf':False})
	if form.validate():
		posts = search_posts(**form.data)
		posts = posts.paginate(page=page_num, per_page=30, error_out=False)

		return render_template('search.html', form=form, posts=posts, title="Search Results", query=request.args)
	return render_template('search.html', form=form, title="Search")


@app.route('/report/<post_num>', methods=['GET', 'POST'])
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

@app.route('/stats')
def stats():
	flag_list = db.session.query(Post.flag, func.count(Post.flag))\
		.group_by(Post.flag)\
		.order_by(func.count(Post.flag).desc()).all()
	flag_list = [(f[0], f[1], app.config['FLAG_MAP'].get(f[0], f[0])) for f in flag_list]

	most_posted = db.session.query(File.filename, func.count(File.filename))\
		.filter(File.filename != 'audioGenericThumb.png', File.filename != 'genericThumb.png')\
		.group_by(File.filename)\
		.order_by(func.count(File.filename).desc()).limit(100)

	return render_template('stats.html', flag_list=flag_list, most_posted=most_posted, title='Stats')

@app.route('/admin', methods=['GET', 'POST'])
@basic_auth.required
def admin():
	session['admin'] = True
	reports = Report.query.filter(Report.dismissed == False).order_by(Report.date.desc()).all()
	return render_template('admin.html', reports=reports)

@app.route('/delete_file/<file_id>', methods=['POST'])
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

@app.route('/delete_files/<post_num>', methods=['POST'])
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

@app.route('/dismiss/<report_id>', methods=['POST'])
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

@app.route('/change_theme')
def change_theme():
	if session.get('theme', None) == 'dark':
		session.pop('theme')
	else:
		session['theme'] = 'dark'

	return redirect(referrer_or_index())
