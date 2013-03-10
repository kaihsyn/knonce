from google.appengine.ext import ndb

class Unit(ndb.Model):
	evernote_token = ndb.StringProperty()