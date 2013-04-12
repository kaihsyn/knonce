from google.appengine.ext import ndb

class Note(ndb.Model):
	guid = ndb.StringProperty()
	usn = ndb.IntegerProperty()
	title = ndb.StringProperty(indexed=False)
	content = ndb.TextProperty()
	updated = ndb.IntegerProperty()
	created = ndb.IntegerProperty()
	tag = ndb.StringProperty(repeated=True)

class Tag(ndb.Model):
	guid = ndb.StringProperty()
	name = ndb.StringProperty()
