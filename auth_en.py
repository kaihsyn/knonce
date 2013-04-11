import sys
if 'lib' not in sys.path:
	sys.path[0:0] = ['lib']

import logging
import webapp2
from google.appengine.ext import ndb

import request

from knonce.unit import Unit
from knonce import helper

class AuthHDL(request.RequestHandler):
	def get(self):
		if not self.logged_in:
			self.redirect('/')

		unit = Unit.query(ancestor=self.current_user.key).fetch(projection=['token'])
		if unit is not None and unit.token != '':
			return self.redirect("/settings")

		client = helper.get_evernote_client()
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
			client = helper.get_evernote_client()
			token = client.get_access_token(
				self.session.get('oauth_token'),
				self.session.get('oauth_token_secret'),
				self.request.get('oauth_verifier')
			)
		except KeyError:
			self.session.add_flash(False, level='en', key='connect')
			logging.error('Failed to retrieve access token data in call back function.')
			return self.redirect('/settings')

		if not self.update_info(client, self.current_user, token):
			self.session.add_flash(False, level='en', key='connect')
			logging.error('Failed to working on unit.')
			return self.redirect('/settings')
		
		self.session.add_flash(True, level='en', key='connect')
		return self.redirect('/settings')

	def update_info(self, client, user, token):

		unit = Unit.get_by_user_key(self.current_user.key)
		if unit is None:
			unit = Unit(parent=self.current_user.key)
			logging.info('Create new Unit')

		unit.token = token
		unit.connected = True

		# update info
		if unit is None:
			return False

		try:
			user_store = client.get_user_store()
			en_user = user_store.getUser()
		except:
			return False

		# update notebook
		unit.username = en_user.username

		#generate an initial id for the unit if alias is already used
		unit.alias = unit.username
		x = 0
		while Unit.query(Unit.alias==unit.alias).count(1) > 0:
			unit.alias = helper.code_generator(size=16)
			x += 1

			if x >= 10:
				logging.info('Failed to generate valid alias.')
				return False
				
		logging.info('Generated alias is %s' % unit.alias)

		""" save Unit """
		try:
			unit.put()
		except:
			return False

		# update user information
		if user.en_name != en_user.name:
			user.en_name = en_user.name
			user.put()

		return True

app = webapp2.WSGIApplication([
	('/auth/evernote', AuthHDL),
	('/auth/evernote/callback', CallbackHDL)
], debug=True, config=request.app_config)
