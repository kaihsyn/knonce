import sys
if 'lib' not in sys.path:
	sys.path[0:0] = ['lib']

import logging
import webapp2
from webapp2_extras import routes

import request
from secrets import HOST

class PostHDL(request.RequestHandler):
	def get(self, alias=None):
		self.render('unit/post.html')

app = webapp2.WSGIApplication([
	routes.DomainRoute('<alias><:(?i)(\.knonce\.com)>', [
	    webapp2.Route('/post', handler='post.PostHDL:get', name='unit-post', methods=['GET'])
	]),
	routes.DomainRoute('localhost', [
	    webapp2.Route('/post', handler='post.PostHDL:get', name='unit-post', methods=['GET'])
	])
], debug=True, config=request.app_config)