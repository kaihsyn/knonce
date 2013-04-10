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