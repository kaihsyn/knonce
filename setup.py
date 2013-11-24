import logging
import re
import request
import webapp2

from evernote.edam.error.ttypes import EDAMErrorCode, EDAMUserException, EDAMSystemException, EDAMNotFoundException
from evernote.edam.type.ttypes import Notebook
from google.appengine.ext.db import TransactionFailedError
from knonce import helper
from knonce.contract import Contract
from knonce.unit import Unit, UnitStatus
from secrets import HOST, DEBUG
from webapp2_extras import routes

class SettingsHDL(request.RequestHandler):
	def get(self):
		if not self.logged_in:
			if self.current_user is not None:
				return self.redirect('/beta')
			else:
				return self.redirect('/')

		""" add user information """
		user = self.current_user
		template_vars = {
			'user': user,
			'host': HOST,
		}

		""" check if still connected """
		unit = Unit.get_by_user_key(user.key)
		if unit is None or unit.token is None:
			logging.info('Missing Evernote authentication info. Redirected to re-authenticate. User: %s'%user.key.urlsafe())
			return self.redirect('/auth/evernote')

		template_vars['unit'] = unit

		""" check flashes """
		flash = self.session.get_flashes(key='connect')
		if len(flash) > 0:
			template_vars['msgs'] = []
			tmp = flash[0]
			if tmp[1] == u'en':
				if tmp[0] == True:
					template_vars['msgs'].append({
						'type':  'success',
						'body':  'We have connected to your Evernote account.'
					})
				else:
					template_vars['msgs'].append({
						'type':  'danger',
						'tab':   'notebook',
						'title': 'Error!',
						'body':  'We failed to connect with your Evernote account. Please give it a try later, or contact support.'
					})

		self.render('setup.html', template_vars)
		return

	def edit(self, target):

		if not self.logged_in:
			self.response.status = '401 Unauthorized'
			return

		template_vars = {'host': HOST}

		""" add user information """
		user = self.current_user
		template_vars['user'] = user

		if target == 'website':
			""" get unit information """
			unit = Unit.get_by_user_key(user.key)
			if unit is None or unit.token is None:
				logging.warning('User attempt to edit Unit that is no longer connected or exist. user.key=%s' % user.key.urlsafe())
				self.response.status = '401 Unautherized'
				return

			template_vars['unit'] = unit

		self.render('setup_%s.html'%target, template_vars)
		return

	def edit_post(self, target):
		if not self.logged_in:
			self.response.status = '401 Unauthorized'
			return

		if target == 'website':
			unit = Unit.get_by_user_key(self.current_user.key)

			if unit is None:
				self.response.status = '404 Not Found'
				return

			put = False

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
				
				unit.alias = alias
				put = True

			if unit.title != helper.escape(self.request.get('title')):
				unit.title = helper.escape(self.request.get('title'))
				put = True

			if unit.sub_title != helper.escape(self.request.get('sub-title')):
				unit.sub_title = helper.escape(self.request.get('sub-title'))
				put = True

			if put:
				try:
					unit.put()
				except TransactionFailedError as e:
					logger.error(e)
					self.response.status = '500 Internal Server Error'
					return

		elif target == 'account':
			self.current_user.name = helper.escape(self.request.get('name'))
			self.current_user.mail = helper.escape(self.request.get('mail'))

			try:
				self.current_user.put()
			except TransactionFailedError:
				self.response.status = '500 Database Error'
				return

		return self.redirect('/setup')

app = webapp2.WSGIApplication([
	routes.DomainRoute('<:(?i)(www\.%s|localhost)>'%HOST, [
		webapp2.Route(r'/setup', handler='setup.SettingsHDL:get', name='get-setup', methods=['GET']),
		webapp2.Route(r'/setup/<target:(website|account)>', handler='setup.SettingsHDL:edit', name='edit-setup', methods=['GET']),
	    webapp2.Route(r'/setup/<target:(website|account)>', handler='setup.SettingsHDL:edit_post', name='update-setup', methods=['POST']),
	])
], debug=DEBUG, config=request.app_config)
