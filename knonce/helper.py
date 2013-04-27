import string
import random

from evernote.api.client import EvernoteClient
from secrets import EN_CONSUMER_KEY, EN_CONSUMER_SECRET

def code_generator(size=16, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))

def get_evernote_client(token=None):
	if token:
		return EvernoteClient(token=token, sandbox=True)
	else:
		return EvernoteClient(
			consumer_key=EN_CONSUMER_KEY,
			consumer_secret=EN_CONSUMER_SECRET,
			sandbox=True
		)

def escape(string):
	return string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\"', '&quot;').replace('\'', '&#x27;').replace('/', '&#x2F;')

def is_reserved_name(name):
	reserved_name = [
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