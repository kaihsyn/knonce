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

		done = self.session.get_flashes(key='done')
		if len(done) > 0:
			logging.info(done[0][0])
			vars['done'] = done[0][0]
			vars['show'] = vars['done']
		
		not_done = done = self.session.get_flashes(key='not_done')
		if len(not_done) > 0:
			vars['not_done'] = not_done[0][0]
			vars['show'] = vars['not_done']

		self.render('settings.html', vars)

	def post(self, target):
		if not self.logged_in:
			self.redirect('/')

		if target == 'account':
			try:
				user = self.current_user
				user.display = self.request.get('display')
				user.email = self.request.get('email')
				user.bio = self.request.get('bio')
				user.put()
			except:
				self.session.add_flash('account', key='not_done')
				self.redirect('/settings')

			self.session.add_flash('account', key='done')

		elif target == 'notebook':
			unit = Unit.get_by_user_key(user.key)

			pass

		self.redirect('/settings')

class NBSelectHDL(request.RequestHandler):
	def get(self):
		if not self.logged_in:
			self.redirect('/')

		self.render('settings.html', vars)



app = webapp2.WSGIApplication([
    ('/settings', SettingsHDL),
    ('/settings/update/(notebook|account)', SettingsHDL),
    ('/select', NBSelectHDL)
	], debug=True, config=request.app_config)
