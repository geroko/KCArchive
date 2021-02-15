from sqlalchemy.orm import lazyload

from src import app, db
from src.models import Post, File

def search_posts(post_num, subject, message, flag, is_op, banned, start_date, end_date, filename, orig_name):
	posts = Post.query
	if post_num:
		posts = posts.filter(Post.post_num == post_num)
	if subject:
		if db.engine.name == 'sqlite':
			posts = posts.filter(Post.subject.contains(subject))
		else:
			posts = posts.filter(Post.subject.match(subject))
	if message:
		if db.engine.name == 'sqlite':
			posts = posts.filter(Post.message.contains(message))
		else:
			posts = posts.filter(Post.message.match(message))
	if flag != 'Show All':
		if flag == 'us.png':
			posts = posts.filter(Post.flag.in_(['us.png'] + [k for k in app.config['STATE_FLAGS'].keys()]))
		elif flag == 'de.png':
			posts = posts.filter(Post.flag.in_(['de.png', '204.png', 'german_empire.png']))
		elif flag == 'it.png':
			posts = posts.filter(Post.flag.in_(['it.png', 'it-204.png']))
		elif flag == 'jp.png':
			posts = posts.filter(Post.flag.in_(['jp.png', 'jp-204.png']))
		elif flag == 'ru.png':
			posts = posts.filter(Post.flag.in_(['ru.png', 'su.png']))
		elif flag == 'fr.png':
			posts = posts.filter(Post.flag.in_(['fr.png'] + [k for k in app.config['FRENCH_FLAGS'].keys()]))
		elif flag == 'by.png':
			posts = posts.filter(Post.flag.in_(['by.png', 'by-luke.png', 'by-25march']))
		else:
			posts = posts.filter(Post.flag == flag)
	if is_op == True:
		posts = posts.filter(Post.is_op == True)
	if banned == True:
		posts = posts.filter(Post.ban_message != None)
	if start_date or end_date:
		posts = posts.order_by(Post.date.desc())
	else:
		posts = posts.order_by(Post.post_num.desc())
	if start_date:
		posts = posts.filter(Post.date > start_date)
	if end_date:
		posts = posts.filter(Post.date < end_date)
	if filename or orig_name:
		posts = posts.group_by(Post.post_num)
	else:
		posts = posts.options(lazyload(Post.files_contained))
	if filename:
		posts = posts.join(Post.files_contained).filter(File.filename.contains(filename))
	if orig_name:
		posts = posts.join(Post.files_contained).filter(File.orig_name.contains(orig_name))
	return posts
