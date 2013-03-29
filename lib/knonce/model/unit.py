from google.appengine.ext import ndb

class Unit(ndb.Model):
	notebook_name = ndb.StringProperty()
	notebook_guid = ndb.StringProperty()
	evernote_token = ndb.StringProperty()

class User():
	first_name = ndb.StringProperty()
	last_name = ndb.StringProperty()
	full_name = name_lower = ndb.ComputedProperty(lambda self: ' '.join([self.first_name, self.last_name]))
	email = ndb.StringProperty()
