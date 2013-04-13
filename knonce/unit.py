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
	def get_by_user_key(user_key):
		try:
			unit = ndb.Key(flat=list(user_key.pairs()).append(('Unit', 'en'))).get()
		except:
			return None
		
		return unit
