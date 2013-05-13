import sys
if 'lib' not in sys.path:
	sys.path[0:0] = ['lib']

import logging
import webapp2
from webapp2_extras import routes
from google.appengine.ext.db import TransactionFailedError
from evernote.edam.type.ttypes import Notebook
from evernote.edam.error.ttypes import EDAMErrorCode, EDAMUserException, EDAMSystemException, EDAMNotFoundException
import request
from secrets import HOST
from knonce.unit import Unit, UnitStatus
from knonce import helper
import re

class SettingsHDL(request.RequestHandler):
	def get(self):
		if not self.logged_in:
			self.redirect('/')
			return

		if not self.current_user.active:
			self.redirect('/beta')
			return

		""" add user information """
		user = self.current_user
		template_vars = {
			'user': user,
			'host': HOST,
		}

		""" check if still connected """
		unit = Unit.get_by_user_key(user.key)
		if unit is not None and unit.token != '':
			if unit.notebook_guid is None or unit.notebook_guid == '':
				self.creatNotebook(unit, False)
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
		return

	def put(self, target):
		if not self.logged_in:
			self.response.status = '401 Unauthorized'
			return

		if not self.current_user.active:
			self.response.status = '401 Unauthorized'
			return

		user = self.current_user
		if target == 'account':
			user.email = helper.escape(self.request.get('email'))

			try:
				user.put()
			except TransactionFailedError:
				self.response.status = '500 Database Error'
				return

		elif target == 'notebook':
			unit = Unit.get_by_user_key(user.key)

			if unit is None:
				self.response.status = '404 Not Found'
				return

			""" check alias """
			if self.request.get('alias'):
				alias = helper.escape(self.request.get('alias')).lower()
				if alias != ''.join(re.findall('[a-z0-9]+', alias.lower())):
					self.response.status = '400 Bad Request'
					self.response.write('Invalid alias name.')
					return

				if unit.alias != alias and (Unit.query(Unit.alias==alias).count(1) > 0 or helper.is_reserved_name(alias)):
					self.response.status = '400 Bad Request'
					self.response.write('Value of \'alias\' is taken.')
					return

				if alias == '':
					self.response.status = '400 Bad Request'
					self.response.write('Value of \'alias\' can\'t be empty.')
					return

			put = False

			if unit.title != helper.escape(self.request.get('title')):
				unit.title = helper.escape(self.request.get('title'))
				put = True

			if unit.sub_title != helper.escape(self.request.get('sub_title')):
				unit.sub_title = helper.escape(self.request.get('sub_title'))
				put = True

			if unit.alias != helper.escape(self.request.get('alias')):
				unit.alias = helper.escape(self.request.get('alias'))
				put = True

			if unit.display != helper.escape(self.request.get('display')):
				unit.display = helper.escape(self.request.get('display'))
				put = True

			if unit.bio != helper.escape(self.request.get('bio')):
				unit.bio = helper.escape(self.request.get('bio'))
				put = True

			if put:
				try:
					unit.put()
				except TransactionFailedError:
					self.response.status = '500 Internal Server Error'
					return

	def nb_list(self):
		if not self.logged_in:
			self.response.status = '401 Unauthorized'
			return

		if not self.current_user.active:
			self.response.status = '401 Unauthorized'
			return

		unit = Unit.get_by_user_key(self.current_user.key)

		if unit.token == '':
			self.response.status = '401 Unauthorized'
			return

		if unit.notebook_guid is not None:
			self.response.status = '401 Unauthorized'
			return

		client = helper.get_evernote_client(token=unit.token)

		try:
			note_store = client.get_note_store()
			notebooks = note_store.listNotebooks()

		except (EDAMUserException, EDAMSystemException) as e:
			logging.error("Evernote API Error: %s on %s." % (e.errorCode, e.parameter))

			if e.errorCode == EDAMErrorCode._NAMES_TO_VALUES['AUTH_EXPIRED']:
				unit = unit.key.get()
				unit.token = ''
				unit.put()
				self.response.status = '401 Unauthorized'
				self.response.write('Evernote Authorization Expired')
				return

			self.response.status = '500 Internal Server Error'
			self.response.write('Evernote Connection Error')
			return

		json_vars = { 'notebooks': [] }
		for nb in notebooks:
			json_vars['notebooks'].append({ 'name': nb.name, 'guid': nb.guid })

		self.render_json(json_vars)
		return

	def nb_name(self):
		if not self.logged_in:
			self.response.status = '401 Unauthorized'
			return

		if not self.current_user.active:
			self.response.status = '401 Unauthorized'
			return

		unit = Unit.get_by_user_key(self.current_user.key)

		if unit.token == '':
			self.response.status = '401 Unauthorized'
			return

		if unit.status == UnitStatus.NotebookNotExist:
			self.response.status = '404 Not Found'
			self.response.write('Notebook Not Found')
			return

		if unit.notebook_guid is None or unit.notebook_guid == '':
			self.creatNotebook(unit, False)

		client = helper.get_evernote_client(token=unit.token)

		try:
			note_store = client.get_note_store()
			notebook = note_store.getNotebook(unit.token, unit.notebook_guid)
		except (EDAMUserException, EDAMSystemException) as e:
			if hasattr(e, 'parameter'):
				logging.error("Evernote API Error: %s %s on %s." % (e.errorCode, EDAMErrorCode._VALUES_TO_NAMES[e.errorCode], e.parameter))
			elif hasattr(e, 'message'):
				logging.error('Evernote Error: %s %s, msg: %s' % (str(e.errorCode), EDAMErrorCode._VALUES_TO_NAMES[e.errorCode], e.message))

			if e.errorCode == EDAMErrorCode._NAMES_TO_VALUES['AUTH_EXPIRED']:
				unit = unit.key.get()
				unit.token = ''
				unit.put()
				self.response.status = '401 Unauthorized'
				self.response.write('Evernote Authorization Expired')
				return

			self.response.status = '500 Internal Server Error'
			self.response.write('Evernote Connection Error')
			return

		except EDAMNotFoundException as e:
			logging.error("EDAMNotFound: %s on %s." % (e.identifier, e.key))

			if e.identifier == 'Notebook.guid':
				unit = unit.key.get()
				unit.status = UnitStatus.NotebookNotExist
				unit.put()
				self.response.status = '404 Not Found'
				self.response.write('Notebook Not Found')
				return

			self.response.status = '500 Internal Server Error'
			self.response.write('Evernote Connection Error')
			return

		if unit.notebook_name != notebook.name:
			unit.notebook_name = notebook.name
			unit.put()

		self.render_json({'name': notebook.name})

	def creatNotebook(self, unit=None, response=True):

		if not self.logged_in:
			self.response.status = '401 Unauthorized'
			return

		if not self.current_user.active:
			self.response.status = '401 Unauthorized'
			return

		if unit is None:
			unit = Unit.get_by_user_key(user.key)

		try:
			client = helper.get_evernote_client(token=unit.token)
			note_store = client.get_note_store()
		except EDAMUserException as e:
			logging.error('Evernote Error: %s %s, parm: %s' % (str(e.errorCode), EDAMErrorCode._VALUES_TO_NAMES[e.errorCode], e.parameter))
			if response:
				self.response.status = '500 Internal Server Error'
			return False
		except EDAMSystemException as e:
			logging.error('Evernote Error: %s %s, msg: %s' % (str(e.errorCode), EDAMErrorCode._VALUES_TO_NAMES[e.errorCode], e.message))
			if response:
				self.response.status = '500 Internal Server Error'
			return False

		retry = 0
		while unit.notebook_guid is None or unit.notebook_guid == '':
			if retry >= 3: 
				name = 'Knonce %s' % helper.code_generator(5)
			elif retry > 0:
				name = 'Knonce %s' % str(retry)
			else:
				name = 'Knonce'
			try:
				nb = Notebook(name=name)
				nb = note_store.createNotebook(unit.token, nb)
			except (EDAMUserException, EDAMSystemException) as e:
				if e.errorCode == EDAMErrorCode._NAMES_TO_VALUES['DATA_CONFLICT'] and e.parameter == 'Notebook.name':
					logging.info('Evernote Error: %s %s, parm: %s' % (str(e.errorCode), EDAMErrorCode._VALUES_TO_NAMES[e.errorCode], e.parameter))
					retry += 1
					if retry > 5:
						if response:
							self.response.status = '500 Internal Server Error'
						return False
					continue
				else:
					logging.error('Evernote Error: %s %s, parm: %s' % (str(e.errorCode), EDAMErrorCode._VALUES_TO_NAMES[e.errorCode], e.parameter))
					if response:
						self.response.status = '500 Internal Server Error'
					return False
			break

		if nb.guid is None:
			if response:
				self.response.status = '500 Internal Server Error'
			return False

		try:
			nb = note_store.getNotebook(unit.token, nb.guid)
		except (EDAMUserException, EDAMSystemException) as e:
			logging.error('Evernote Error: %s %s, parm: %s' % (str(e.errorCode), EDAMErrorCode._VALUES_TO_NAMES[e.errorCode], e.parameter))
			if response:
				self.response.status = '500 Internal Server Error'
			return False
		except EDAMNotFoundException as e:
			logging.error('EDAMNotFound identifier: %s, key: %s' % (exception.identifier, exception.key))
			if response:
				self.response.status = '500 Internal Server Error'
			return False

		unit.notebook_name = nb.name
		unit.notebook_guid = nb.guid

		unit.put()
		return True

app = webapp2.WSGIApplication([
	routes.DomainRoute('<:(?i)(www\.%s|localhost)>'%HOST, [
		webapp2.Route(r'/settings', handler='settings.SettingsHDL:get', name='get-settings', methods=['GET']),
	    webapp2.Route(r'/settings/<target:(notebook|account)>', handler='settings.SettingsHDL:put', name='update-settings', methods=['PUT']),
	    webapp2.Route(r'/settings/notebook/name', handler='settings.SettingsHDL:nb_name', name='update-get-notebook-name', methods=['GET']),
	    webapp2.Route(r'/settings/notebook/list', handler='settings.SettingsHDL:nb_list', name='get-notebook-list', methods=['GET']),
	])
], debug=True, config=request.app_config)
