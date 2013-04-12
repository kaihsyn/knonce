from google.appengine.ext import ndb

class Unit(ndb.Model):
	username = ndb.StringProperty(indexed = False)
	user_id = ndb.IntegerProperty()
	alias = ndb.StringProperty(default='')
	notebook_name = ndb.StringProperty(indexed = False)
	notebook_guid = ndb.StringProperty()
	token = ndb.StringProperty(default='')
	connected = ndb.BooleanProperty(default=False)

	@staticmethod
	def get_by_user_key(user_key, projection=None):
		try:
			unit = Unit.query(ancestor=user_key).fetch(1, projection=None)
		except:
			return None
		
		return unit[0] if len(unit) > 0 else None
