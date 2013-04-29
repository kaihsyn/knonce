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
	sub_match = re.findall('<en-note(.*?)>',raw,re.M|re.I)
	for en_sub in sub_match:
		split = re.split('[ =]',en_sub)
		temp_str = ""
		insert = False
		for s in split:
			if s != "":
				if insert:
					insert = False
					temp_str+="="+s
				elif s == 'title':
					insert = True
					temp_str+=" "+s
				elif s == 'style':
					insert = True
					temp_str+=" "+s
				elif s == 'lang':
					insert = True
					temp_str+=" "+s
				elif s == 'xml:lang':
					insert = True
					temp_str+=" "+s
		raw = raw.replace(en_sub,temp_str)
	raw = raw.replace('en-note','div')

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

