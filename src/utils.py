import re
import bleach

from flask import request, url_for

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

def format_bytes(num):
	for unit in ['B','KB','MB','GB','TB']:
		if abs(num) < 1024.0:
			return f'{num:.2f} {unit}'
		num /= 1024.0
	return num

def get_ip_address():
	if "X-Forwarded-For" in request.headers:
		return request.headers.getlist("X-Forwarded-For")[0].split()[-1]
	return request.environ["REMOTE_ADDR"]

def format_message(message):
	formatted = re.sub(r'>', r'&gt;', message)
	formatted = re.sub(r'<', r'&lt;', formatted)
	formatted = re.sub(r'(&gt;&gt;(\d+))', r'<a href="#\2" class="reply-link">\1</a>', formatted)
	formatted = re.sub(r'^(&gt;.*)$', r'<span class="greentext">\1</span>', formatted, flags=re.MULTILINE)
	formatted = re.sub(r'^(&lt;.*)$', r'<span class="orangetext">\1</span>', formatted, flags=re.MULTILINE)
	formatted = re.sub(r'\[spoiler\](.*)\[/spoiler\]', r'<span class="spoiler">\1</span>', formatted)
	formatted = re.sub(r'\*\*(.*)\*\*', r'<span class="spoiler">\1</span>', formatted)
	formatted = re.sub(r'==(.*)==', r'<span class="redtext">\1</span>', formatted)
	formatted = re.sub(r'\[b\](.*)\[/b\]', r'<b>\1</b>', formatted)
	formatted = re.sub(r'\'\'\'(.*)\'\'\'', r'<b>\1</b>', formatted)
	formatted = re.sub(r'\[i\](.*)\[/i\]', r'<i>\1</i>', formatted)
	formatted = re.sub(r'\[code\](.*)\[/code\]', r'<code>\1</code>', formatted, flags=re.DOTALL)
	formatted = re.sub(r'\[u\](.*)\[/u\]', r'<u>\1</u>', formatted)
	formatted = re.sub(r'__(.*)__', r'<u>\1</u>', formatted)
	formatted = re.sub(r'\[s\](.*)\[/s\]', r'<s>\1</s>', formatted)
	formatted = re.sub(r'~~(.*)~~', r'<s>\1</s>', formatted)
	formatted = re.sub(r'\n', r'<br>', formatted)

	formatted = bleach.clean(formatted, tags=['br', 'a', 'span', 'b', 'i', 'code', 'u', 's'], attributes=['class', 'id', 'href'])
	formatted = bleach.linkify(formatted, callbacks=[])
	
	return formatted

def referrer_or_index():
	if request.referrer != None:
		return request.referrer
	else:
		return url_for('index')
