import logging
from google.appengine.ext import ndb

class UnitStatus():
	Active, NotebookNotExist = range(2)

class Unit(ndb.Model):

	""" unit information """
	title = ndb.StringProperty()
	sub_title = ndb.StringProperty()
	alias = ndb.StringProperty()

	""" evernote information """
	user_id = ndb.IntegerProperty()
	token = ndb.StringProperty()
	
	""" unit status """
	name_count = ndb.IntegerProperty(default=0)

	@staticmethod
	def get_by_user_key(user_key):
		try:
			unit = ndb.Key(flat=list(user_key.flat())+['Unit', 'en']).get()
		except:
			return None
		
		return unit
