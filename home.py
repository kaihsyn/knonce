import sys
if 'lib' not in sys.path:
	sys.path[0:0] = ['lib']

import logging
import webapp2

import request

class MainHandler(request.RequestHandler):
	def get(self):
		self.render('home.html')

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True, config=request.app_config)
