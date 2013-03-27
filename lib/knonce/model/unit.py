from google.appengine.ext import ndb

class Unit(ndb.Model):
	first_name = ndb.StringProperty()
	last_name = ndb.StringProperty()
	full_name = name_lower = ndb.ComputedProperty(lambda self: ' '.join([self.first_name, self.last_name]))

	notebook_name = ndb.StringProperty()
	notebook_guid = ndb.StringProperty()
	evernote_token = ndb.StringProperty()

class AuthService():
	'Google' = range(1)

def v_auth_svc(prop, value):
	if value < 0 or value > 0:
		raise ValueError("Illegal authentication service.")
	return value

class Auth(ndb.Model):
	service = ndb.IntegerProperty(validator=v_auth_svc)
	info = ndb.StringProperty()