import sys
if 'lib' not in sys.path:
	sys.path[0:0] = ['lib']

import logging
import webapp2
import request

from google.appengine.ext.db import TransactionFailedError

from knonce.unit import Unit

class SettingsHDL(request.RequestHandler):
	def get(self):
		if not self.logged_in:
			self.redirect('/')

		user = self.current_user
		vars = {
			'unit': Unit.get_by_user_key(user.key),
			'user': user
		}

		self.render('settings.html', vars)

	def post(self, target):
		if not self.logged_in:
			self.redirect('/')

		if target == 'account':
			user = self.current_user
			try:
				user.display = self.request.get('display')
				user.email = self.request.get('email')
				user.bio = self.request.get('bio')
				user.put()
			except TransactionFailedError:
				self.response.status = '500 Database Error'

		elif target == 'notebook':
			unit = Unit.get_by_user_key(user.key)

			if unit is None:
				self.response.status = '400 Unit Not Found'

			try:
				unit.alias = self.request.get('alias')
				unit.put()
			except TransactionFailedError:
				self.response.status = '500 Database Error'

class NBSelectHDL(request.RequestHandler):
	def get(self):
		if not self.logged_in:
			self.redirect('/')

		self.render('settings.html', vars)

app = webapp2.WSGIApplication([
	webapp2.Route(r'/settings', handler='settings.SettingsHDL:get', name='get-settings', methods=['GET']),
    webapp2.Route(r'/settings/<target:(notebook|account)>', handler='settings.SettingsHDL:post', name='update-settings', methods=['POST']),
    (r'/select', NBSelectHDL)
	], debug=True, config=request.app_config)
