import sys
if 'lib' not in sys.path:
	sys.path[0:0] = ['lib']

import logging
import webapp2
from webapp2_extras import routes

import request
from secrets import HOST

from knonce.note import Note
from knonce.unit import Unit

class PostHDL(request.RequestHandler):
	def get(self, alias=None, short=None):

		""" check required data """
		if alias is None:
			return self.redirect('http://www.knonce.com/')

		""" get unit """
		unit = Unit.query(Unit.alias==alias.lower()).get()
		if unit is None:
			return self.redirect('http://www.knonce.com/')

		""" check required data """
		if short is None:
			return self.redirect('/')

		""" get note """
		logging.info(short.lower())
		note = Note.query(Note.short==short.lower()).get()
		if note is None:
			return self.redirect('/')

		pageval = { 'host': 'www.%s'%HOST, 'unit': unit, 'note': note }
		self.render('unit/post.html', pageval)

app = webapp2.WSGIApplication([
	routes.DomainRoute('<alias><:(?i)(\.knonce\.com)>', [
	    webapp2.Route('/post/<short>', handler='post.PostHDL:get', name='unit-post', methods=['GET'])
	]),
	routes.DomainRoute('localhost', [
	    webapp2.Route('/post/<short>', handler='post.PostHDL:get', name='unit-post', methods=['GET'])
	])
], debug=True, config=request.app_config)