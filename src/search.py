from src.models import Post, File

def search_posts(post_num, subject, message, flag, is_op, banned, start_date, end_date, filename, orig_name):
	posts = Post.query.group_by(Post.post_num).order_by(Post.date.desc())
	if post_num:
		posts = posts.filter(Post.post_num == post_num)
	if subject:
		posts = posts.filter(Post.subject.contains(subject))
	if message:
		posts = posts.filter(Post.message.contains(message))
	if flag != 'Show All':
		posts = posts.filter(Post.flag == flag)
	if is_op == True:
		posts = posts.filter(Post.is_op == True)
	if banned == True:
		posts = posts.filter(Post.ban_message != None)
	if start_date:
		posts = posts.filter(Post.date > start_date)
	if end_date:
		posts = posts.filter(Post.date < end_date)
	if filename:
		posts = posts.join(Post.files_contained).filter(File.filename.contains(filename))
	if orig_name:
		posts = posts.join(Post.files_contained).filter(File.orig_name.contains(orig_name))
	return posts
