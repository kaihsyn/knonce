from google.appengine.ext import ndb

class Post(ndb.Model):
	guid = ndb.StringProperty()
	title = ndb.StringProperty()
	content = ndb.TextProperty()
	updated = ndb.IntegerProperty()
	created = ndb.IntegerProperty()