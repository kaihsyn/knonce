import time
import logging
import re

""" lazy parse for content """
def parse_evernote(raw):
	start_time = time.time()

	""" replace xml declaration """
	raw = re.sub('^(<\?xml +)( *(version|encoding) *= *"[A-Za-z0-9-._]*")* *\?>\s*', '', raw, 1)

	""" replace doctype """
	raw = re.sub('^(<\!DOCTYPE +)[ A-Za-z0-9\."\-_:\/&=%]*>\s*', '', raw, 1)

	""" replace en-note """
	subn = re.subn('<en\-note( +((?!>).)*)* *>', '', raw, 1)
	if subn[1] > 0:
		raw = subn[0]
		raw = re.sub('</en\-note *>', '', raw, 1)
	else:
		raw = re.sub('<en\-note */>', '', raw, 1)

	""" replace en-crypt """
	raw = re.sub('<en\-crypt( +((?!>).)*)* *>((?!(</en\-crypt *>)).)*</en\-crypt *>', '', raw)

	""" replace en-todo """
	raw = re.sub('<en\-todo( +checked *= *"false")? */>', '<i class="icon-check-empty"></i>', raw)
	raw = re.sub('<en\-todo( +checked *= *"false")? *></en-todo *>', '<i class="icon-check-empty"></i>', raw)

	raw = re.sub('<en\-todo +checked *= *"true" */>', '<i class="icon-check"></i>', raw)
	raw = re.sub('<en\-todo +checked *= *"true" *></en-todo *>', '<i class="icon-check"></i>', raw)

	""" replace en-media """
	raw = re.sub('<en\-media( +((?!>).)*)* */>', '', raw)
	raw = re.sub('<en\-media( +((?!>).)*)* *></en-media *>', '', raw)

	logging.info('parse time: %s ms.' % str((time.time() - start_time) * 1000))

	return raw

def create_summary(raw):

	""" remove all tags """
	raw = re.sub('<((?![<>]).)*>', '', raw)

	return raw[:280]
