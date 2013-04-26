from google.appengine.ext import ndb

class Note(ndb.Model):
	usn = ndb.IntegerProperty(indexed=False)
	short = ndb.StringProperty(required=True)
	title = ndb.StringProperty(default='', indexed=False)
	summary = ndb.TextProperty(default='')
	content = ndb.TextProperty(default='')
	updated = ndb.IntegerProperty(indexed=False)
	created = ndb.IntegerProperty()
	tag = ndb.StringProperty(repeated=True)

	first_add = ndb.DateTimeProperty(auto_now_add=True)

class Tag(ndb.Model):
	guid = ndb.StringProperty()
	name = ndb.StringProperty()
	