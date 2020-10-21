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
