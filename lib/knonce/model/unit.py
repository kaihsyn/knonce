from google.appengine.ext import ndb

class Unit(ndb.Model):
	evernote_key = ndb.StringProperty()