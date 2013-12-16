import logging
import webapp2
from webapp2_extras import routes

import request
from secrets import HOST, DEBUG

class MainHDL(request.RequestHandler):
	def get(self):
		self.render('home.html')

	def beta(self):
		self.render('home.html', {'beta':True})

app = webapp2.WSGIApplication([
	routes.DomainRoute('<:(?i)(www\.%s)>'%HOST, [
	    webapp2.Route('/', handler='home.MainHDL:get', name='main-page', methods=['GET']),
	    webapp2.Route('/beta', handler='home.MainHDL:beta', name='main-page-w-beta', methods=['GET'])
	]),
	routes.DomainRoute('<alias><:(?i)(\.%s)>'%HOST, [
	    webapp2.Route('/', handler='unit_home.MainHDL:get', name='unit-main-page', methods=['GET'])
	]),
	routes.DomainRoute('localhost', [
	    #webapp2.Route('/', handler='unit_home.MainHDL:get', name='unit-main-page', methods=['GET']),
		webapp2.Route('/', handler='home.MainHDL:get', name='main-page', methods=['GET']),
	    webapp2.Route('/beta', handler='home.MainHDL:beta', name='main-page-w-beta', methods=['GET'])
	])
], debug=DEBUG, config=request.app_config)
