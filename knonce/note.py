from google.appengine.ext import ndb

class Note(ndb.Model):
	usn = ndb.IntegerProperty(indexed=False)
	short = ndb.StringProperty(required=True)
	title = ndb.StringProperty(default='')
	summary = ndb.StringProperty(default='')
	content = ndb.TextProperty(default='')
	updated = ndb.IntegerProperty(indexed=False)
	created = ndb.IntegerProperty(indexed=False)
	tag = ndb.StringProperty(repeated=True)

	date = ndb.DateTimeProperty(auto_now_add=True)

class Tag(ndb.Model):
	guid = ndb.StringProperty()
	name = ndb.StringProperty()
	