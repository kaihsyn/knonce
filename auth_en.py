import sys
if 'lib' not in sys.path:
	sys.path[0:0] = ['lib']

import logging
import string
import webapp2
from webapp2_extras import routes
from google.appengine.ext import ndb
from evernote.edam.error.ttypes import EDAMErrorCode, EDAMUserException, EDAMSystemException, EDAMNotFoundException
from evernote.edam.type.ttypes import Notebook
import request
from secrets import HOST
from knonce.unit import Unit
from knonce import helper

class AuthHDL(request.RequestHandler):
	def get(self):
		if not self.logged_in:
			self.redirect('/')

		unit = Unit.get_by_user_key(self.current_user.key)
		if unit is not None and unit.token != '':
			return self.redirect("/settings")

		client = helper.get_evernote_client()
		callbackUrl = 'http://%s/auth/evernote/callback' % self.request.host
		request_token = client.get_request_token(callbackUrl)

		# Save the request token information for later
		try:
			self.session['oauth_token'] = request_token['oauth_token']
			self.session['oauth_token_secret'] = request_token['oauth_token_secret']
		except KeyError:
			self.session.add_flash(False, level='en', key='connect')
			logging.error('Failed to retrieve access token data in auth function.')
			return self.redirect('/settings')

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
			unit = Unit(id='en', parent=self.current_user.key)
			logging.info('Create new Unit')

		try:
			user_store = client.get_user_store()
			en_user = user_store.getUser()
		except (EDAMUserException, EDAMSystemException) as e:
			logging.error('Evernote Error: %s %s, parm: %s' % (str(e.errorCode), EDAMErrorCode._VALUES_TO_NAMES[e.errorCode], e.parameter))
			return False

		unit.token = token
		unit.username = en_user.username
		unit.user_id = en_user.id

		#generate an initial id for the unit if alias is already used
		unit.alias = unit.username.lower()
		x = 0
		while Unit.query(Unit.alias==unit.alias).count(1) > 0 or helper.is_reserved_name(unit.alias):
			
			if x >= 10:
				logging.info('Failed to generate valid alias.')
				return False

			unit.alias = helper.code_generator(size=8, chars=string.ascii_lowercase + string.digits)
			x += 1
				
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
	routes.DomainRoute('<:(?i)(www\.%s|localhost)>'%HOST, [
		webapp2.Route(r'/auth/evernote', handler='auth_en.AuthHDL:get', name='auth-evernote', methods=['GET']),
		webapp2.Route(r'/auth/evernote/callback', handler='auth_en.CallbackHDL:get', name='auth-evernote-callback', methods=['GET']),
	]),
], debug=True, config=request.app_config)
