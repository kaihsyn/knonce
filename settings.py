import sys
if 'lib' not in sys.path:
	sys.path[0:0] = ['lib']

import logging
import webapp2
import request

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

		connect = True
		connect_set = False
		for key in ['connect_evernote', 'update_info']:
			flash = self.session.get_flashes(key=key)
			if len(flash) != 0:
				connect_set = True
				connect &= flash[0][0]
		if connect_set is True:
			vars['connect'] = connect

		self.render('settings.html', vars)

	def post(self):
		if not self.logged_in:
			self.redirect('/')

		user = self.current_user
		user.display = self.request.get('display')
		user.email = self.request.get('email')
		user.bio = self.request.get('bio')
		user.put()

		vars = {
			'unit': Unit.get_by_user_key(user.key),
			'user': user,
			'show': 'account'
		}

		self.render('settings.html', vars)


app = webapp2.WSGIApplication([
    ('/settings', SettingsHDL)
	], debug=True, config=request.app_config)
