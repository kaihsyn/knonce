from google.appengine.ext import ndb

class Unit(ndb.Model):
	username = ndb.StringProperty()
	alias = ndb.StringProperty(default='')
	notebook_name = ndb.StringProperty()
	notebook_guid = ndb.StringProperty()
	token = ndb.StringProperty(default='')

	@staticmethod
	def get_by_user_key(user_key):
		try:
			unit = Unit.query(ancestor=user_key).get()
		except:
			return None
		return unit
