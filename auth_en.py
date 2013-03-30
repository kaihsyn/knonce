import sys
if 'lib' not in sys.path:
	sys.path[0:0] = ['lib']

import logging
import webapp2

import request

from evernote.api.client import EvernoteClient
from secrets import EN_CONSUMER_KEY, EN_CONSUMER_SECRET
from knonce.unit import Unit

def get_evernote_client(token=None):
	if token:
		return EvernoteClient(token=token, sandbox=True)
	else:
		return EvernoteClient(
			consumer_key=EN_CONSUMER_KEY,
			consumer_secret=EN_CONSUMER_SECRET,
			sandbox=True
		)

class AuthHDL(request.RequestHandler):
	def get(self):
		if not self.logged_in:
			self.redirect('/')

		client = get_evernote_client()
		callbackUrl = 'http://%s/auth/evernote/callback' % self.request.host
		request_token = client.get_request_token(callbackUrl)

		# Save the request token information for later
		self.session['oauth_token'] = request_token['oauth_token']
		self.session['oauth_token_secret'] = request_token['oauth_token_secret']

		# Redirect the user to the Evernote authorization URL
		return self.redirect(client.get_authorize_url(request_token))

class CallbackHDL(request.RequestHandler):
	def get(self):
		if not self.logged_in:
			self.redirect('/')

		try:
			client = get_evernote_client()
			token = client.get_access_token(
				self.session.get('oauth_token'),
				self.session.get('oauth_token_secret'),
				self.request.get('oauth_verifier')
			)
		except KeyError:
			self.session.add_flash(False, key='connect_evernote')
			return self.redirect('/settings')

		unit = Unit.get_by_user_key(self.current_user.key)
		if unit is None:
			unit = Unit(parent=self.current_user.key)

		unit.token = token
		unit.put()

		self.session.add_flash(True, key='connect_evernote')
		self.session.add_flash(self.update_info(client), key='update_info')

		return self.redirect('/settings')

	def update_info(self, client):
		# update info
		user = self.current_user
		unit = Unit.get_by_user_key(user.key)
		if unit is None:
			return False

		try:
			user_store = client.get_user_store()
			en_user = user_store.getUser()
		except:
			return False

		# update notebook
		unit.username = en_user.username
		unit.put()

		# update user information
		user.en_name = en_user.name
		user.put()

		return True

app = webapp2.WSGIApplication([
	('/auth/evernote', AuthHDL),
	('/auth/evernote/callback', CallbackHDL)
], debug=True, config=request.app_config)
