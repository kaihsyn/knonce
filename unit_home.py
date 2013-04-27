import sys
if 'lib' not in sys.path:
	sys.path[0:0] = ['lib']

import logging
import request
import datetime
from secrets import HOST
from knonce.note import Note
from knonce.unit import Unit
from collections import OrderedDict

class MainHDL(request.RequestHandler):
	def get(self, alias=None):

		if alias is None:
			return self.redirect('http://www.knonce.com/')

		""" get unit """
		unit = Unit.query(Unit.alias==alias).get()
		if unit is None:
			return self.redirect('http://www.knonce.com/')

		""" grab latest ten notes """
		notes, next_curs, more = Note.query(ancestor=unit.key).order(Note.first_add).fetch_page(10, projection=['date', 'short', 'title', 'summary'])

		pageval = {
			'unit': unit
			'host': 'www.%s'%HOST,
			'cursor': next_curs.urlsafe(),
			'notes': OrderedDict() }

		for note in notes:
			if note.date not in pageval['notes']:
				pageval['notes'][note.date] = []
			pageval['notes'][note.date].append(note)

		self.render('unit/home.html', pageval)

