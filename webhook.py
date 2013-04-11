import webapp2
import logging

from google.appengine.api import taskqueue
from secrets import EN_WEBHOOK

class EvernoteWebhookHDL(webapp2.RequestHandler):
    def get(self):
    	miss_var = False

    	if self.request.get('userId') and self.request.get('userId') != '':
    		user_id = self.request.get('userId')
    	else:
    		user_id = '[no userId]'
    		miss_var = True

    	if self.request.get('guid') and self.request.get('guid') != '':
    		guid = self.request.get('guid')
    	else:
    		guid = '[no guid]'
    		miss_var = True

    	if self.request.get('reason'):
    		if self.request.get('reason') == 'create' or self.request.get('reason') == 'update':
    			reason = self.request.get('reason')
    		else:
    			reason = '[wrong format reason: %s]' % self.request.get('reason')
	    		miss_var = True
    	else:
    		reason = '[no reason]'
    		miss_var = True

    	if miss_var:
    		logging.error('Evernote Webhook: %s %s %s' % (user_id, guid, reason))
    	else:
    		logging.info('Evernote Webhook: %s %s %s' % (user_id, guid, reason))

    	#taskqueue.add(queue_name='sync-evernote', url='/sync/evernote', params={'key': 'abcdgogady'})

app = webapp2.WSGIApplication([
    webapp2.Route('/hook/%s'%EN_WEBHOOK, handler='webhook.EvernoteWebhookHDL:get', name='evernote-webhook', methods=['GET'])
], debug=True)
