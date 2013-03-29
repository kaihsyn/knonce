import logging
import webapp2
import jinja2
import os

import sys
sys.path.append('./lib')

from knonce import session
from evernote.api.client import EvernoteClient

from secrets import EN_CONSUMER_KEY, EN_CONSUMER_SECRET

def get_evernote_client(token=None):
	if token:
		return EvernoteClient(token=token, sandbox=True)
	else:
		return EvernoteClient(
			consumer_key=EN_CONSUMER_KEY,
			consumer_secret=EN_CONSUMER_SECRET,
			sandbox=True
		)

class AuthHDL(session.RequestHandler):
	def get(self):
		client = get_evernote_client()
		callbackUrl = 'http://%s/auth/callback' % (self.request.host, )
		request_token = client.get_request_token(callbackUrl)

		# Save the request token information for later
		self.session['oauth_token'] = request_token['oauth_token']
		self.session['oauth_token_secret'] = request_token['oauth_token_secret']

		# Redirect the user to the Evernote authorization URL
		return self.redirect(client.get_authorize_url(request_token))

class CallbackHDL(session.RequestHandler):
	def get(self):
		try:
			client = get_evernote_client()
			logging.info(client.get_access_token(
				self.session.get('oauth_token'),
				self.session.get('oauth_token_secret'),
				self.request.get('oauth_verifier')
			))
		except KeyError:
			return self.redirect('/')
		
		"""
		note_store = client.get_note_store()
		notebooks = note_store.listNotebooks()

		return render_to_response('oauth/callback.html', {'notebooks': notebooks})
		"""
		return self.redirect('/')

app = webapp2.WSGIApplication([
	('/auth', AuthHDL),
	('/auth/callback', CallbackHDL)
	], debug=True, config=session.session_config)

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))