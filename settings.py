import sys
if 'lib' not in sys.path:
	sys.path[0:0] = ['lib']

import logging
import webapp2
from google.appengine.ext.db import TransactionFailedError

from evernote.edam import error

import request
from knonce.unit import Unit
from knonce import helper

class SettingsHDL(request.RequestHandler):
	def get(self):
		if not self.logged_in:
			self.redirect('/')

		""" add user information """
		user = self.current_user
		template_vars = {
			'user': user,
			'host': self.request.host,
		}

		""" check if still connected """
		unit = Unit.get_by_user_key(user.key)
		if unit is not None and unit.token != '':
			template_vars['unit'] = unit

		""" check flashes """
		flash = self.session.get_flashes(key='connect')
		if len(flash) > 0:
			tmp = flash[0]
			if tmp[1] == u'en':
				if tmp[0] == True:
					template_vars['msg'] = {
						'type':  'success',
						'tab':   'notebook',
						'title': 'Success!',
						'body':  'We have connected to your Evernote account.'
					}
				else:
					template_vars['msg'] = {
						'type':  'danger',
						'tab':   'notebook',
						'title': 'Error!',
						'body':  'We failed to connect with your Evernote account. Please give it a try later, or contact support.'
					}

		self.render('settings.html', template_vars)

	def put(self, target):
		if not self.logged_in:
			self.redirect('/')

		user = self.current_user
		if target == 'account':
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
				self.response.status = '404 Unit Not Found'

			""" check alias """
			if self.request.get('alias'):
				if unit.alias != self.request.get('alias') and Unit.query(Unit.alias==unit.alias).count(1) > 0:
					self.response.status = '400 Value Of \'alias\' Is Taken'
				elif self.request.get('alias') == '':
					self.response.status = '400 Value Of \'alias\' Can\'t Be Empty'

			try:
				unit.alias = self.request.get('alias')
				unit.notebook_name = self.request.get('notebook_name')
				unit.notebook_guid = self.request.get('notebook_guid')
				unit.put()
			except TransactionFailedError:
				self.response.status = '500 Database Error'

	def nb_list(self):
		unit = Unit.get_by_user_key(self.current_user.key)
		client = helper.get_evernote_client(token=unit.token)

		note_store = client.get_note_store()
		try:
			notebooks = note_store.listNotebooks()
		except error.ttypes.EDAMUserException, e:
			logging.error("Evernote API Error: %s on %s." % (e.errorCode, e.parameter))
			self.response.status = '500 Evernote Connection Error'
			return

		except error.ttypes.EDAMSystemException, e:
			logging.error("Evernote API Error: %s with message \"%s\"." % (e.errorCode, e.message))
			self.response.status = '500 Evernote Connection Error'
			return

		json_vars = { 'notebooks': [] }
		for nb in notebooks:
			json_vars['notebooks'].append({ 'name': nb.name, 'guid': nb.guid })

		self.render_json(json_vars)

class NBSelectHDL(request.RequestHandler):
	def get(self):
		if not self.logged_in:
			self.redirect('/')

		self.render('settings.html', vars)

app = webapp2.WSGIApplication([
	webapp2.Route(r'/settings', handler='settings.SettingsHDL:get', name='get-settings', methods=['GET']),
    webapp2.Route(r'/settings/<target:(notebook|account)>', handler='settings.SettingsHDL:put', name='update-settings', methods=['PUT']),
    webapp2.Route(r'/settings/notebook_list', handler='settings.SettingsHDL:nb_list', name='get-notebook-list', methods=['GET']),
	], debug=True, config=request.app_config)
