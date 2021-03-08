from sqlalchemy.orm import lazyload
from sqlalchemy.sql import text

from src import app, db
from src.models import Post, File

def search_posts(post_num, subject, message, flag, is_op, banned, start_date, end_date, filename, orig_name, order):
	posts = Post.query
	if order == 'desc' or order == None:
		posts = posts.order_by(Post.date.desc())
	elif order == 'asc':
		posts = posts.order_by(Post.date)
	if post_num:
		posts = posts.filter(Post.post_num == post_num)
	if subject:
		posts = posts.filter(text(f"tsv_subject @@ websearch_to_tsquery('english', :subject)").params(subject=subject))
	if message:
		posts = posts.filter(text(f"tsv_message @@ websearch_to_tsquery('english', :message)").params(message=message))
	if flag and flag != 'Show All':
		posts = posts.filter(Post.flag == flag)
	if is_op == True:
		posts = posts.filter(Post.is_op == True)
	if banned == True:
		posts = posts.filter(Post.ban_message != None)
	if start_date:
		posts = posts.filter(Post.date > start_date)
	if end_date:
		posts = posts.filter(Post.date < end_date)
	if filename or orig_name:
		posts = posts.join(Post.files_contained).group_by(Post.post_num)
	else:
		posts = posts.options(lazyload(Post.files_contained))
	if filename:
		posts = posts.filter(File.filename == 't_' + filename)
	if orig_name:
		posts = posts.filter(File.orig_name.contains(orig_name))
	return posts
