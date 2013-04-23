import sys
if 'lib' not in sys.path:
	sys.path[0:0] = ['lib']

import logging
import request

class MainHDL(request.RequestHandler):
	def get(self, alias=None):
		self.render('unit/home.html')

