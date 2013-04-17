import logging
from google.appengine.ext import ndb

class UnitStatus():
	Active, NotebookNotExist = range(2)

class Unit(ndb.Model):
	username = ndb.StringProperty()
	user_id = ndb.IntegerProperty()
	alias = ndb.StringProperty(default='')
	notebook_name = ndb.StringProperty()
	notebook_guid = ndb.StringProperty()
	token = ndb.StringProperty(default='')
	name_count = ndb.IntegerProperty(default=0, indexed = False)
	status = ndb.IntegerProperty(default=UnitStatus.Active)

	@staticmethod
	def get_by_user_key(user_key):
		try:
			unit = ndb.Key(flat=list(user_key.flat())+['Unit', 'en']).get()
		except:
			return None
		
		return unit
