import sys
if 'lib' not in sys.path:
	sys.path[0:0] = ['lib']

import logging
import request

from secrets import HOST

class MainHDL(request.RequestHandler):
	def get(self, alias=None):
		pageval = { 'host': 'www.%s'%HOST }
		self.render('unit/home.html', pageval)

