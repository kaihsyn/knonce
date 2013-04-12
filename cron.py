import webapp2
import logging

from google.appengine.api import taskqueue

class CronSyncEvernoteHDL(webapp2.RequestHandler):
    def get(self):
    	logging.info('Cron Sync Evernote')

app = webapp2.WSGIApplication([
    ('/cron/sync-evernote', CronSyncEvernoteHDL)
], debug=True)