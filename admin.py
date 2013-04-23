import webapp2
import logging
from webapp2_extras import routes
from google.appengine.ext import ndb
from webapp2_extras.appengine.auth.models import User

import request

from secrets import HOST
from knonce.unit import Unit, UnitStatus
from knonce.note import Note

class AdminHDL(request.RequestHandler):
	def reset_unit(self, alias):
		unit = Unit.query(Unit.alias==alias).get()
		unit.notebook_name = None
		unit.notebook_guid = None
		unit.status == UnitStatus.Active
		unit.put()

		self.response.write('done!')

	def active_user(self, key):
		user = ndb.Key(urlsafe=key).get()
		user.active = True
		user.put()

		self.response.write('done!')

app = webapp2.WSGIApplication([
	routes.DomainRoute('<:(?i)(www.%s|localhost)>'%HOST, [
		webapp2.Route('/admin/reset/unit/<alias>', handler='admin.AdminHDL:reset_unit', name='reset-unit', methods=['GET', 'POST']),
		#webapp2.Route('/admin/active/<key>', handler='admin.AdminHDL:active_user', name='active-user', methods=['GET', 'POST']),
	]),
], debug=True, config=request.app_config)
