import string
import random

from secrets import EN_CONSUMER_KEY, EN_CONSUMER_SECRET

def code_generator(size=16, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))

def escape(string):
	return string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\"', '&quot;').replace('\'', '&#x27;').replace('/', '&#x2F;')

def is_reserved_name(name):
	reserved_name = [
		'mxchar',
		'kaihsyn',
		'knonce',
		'admin',
		'control',
		'register',
		'login',
		'fuck',
		'suck',
		'logout',
		'news',
		'announce',
		'blog',
		'mail',
		'web',
		'offer',
		'group',
		'develop',
		'dev',
		'api',
		'shit',
		'register',
		'contact',
		'support',
	]
	return name in reserved_name