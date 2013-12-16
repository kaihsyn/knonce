import logging
import request
import webapp2

from knonce.note import Note
from knonce.unit import Unit
from secrets import HOST, DEBUG
from webapp2_extras import routes

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
], debug=DEBUG, config=request.app_config)