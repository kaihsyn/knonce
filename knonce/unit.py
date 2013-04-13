import logging
from google.appengine.ext import ndb

class Unit(ndb.Model):
	username = ndb.StringProperty(indexed = False)
	user_id = ndb.IntegerProperty()
	alias = ndb.StringProperty(default='')
	notebook_name = ndb.StringProperty(indexed = False)
	notebook_guid = ndb.StringProperty()
	token = ndb.StringProperty(default='')

	@staticmethod
	def get_by_user_key(user_key):
		try:
			unit = ndb.Key(flat=list(user_key.flat())+['Unit', 'en']).get()
		except:
			return None
		
		return unit
