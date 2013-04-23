import webapp2
import logging
from webapp2_extras import routes

import request

from google.appengine.api import taskqueue
from secrets import HOST, EN_WEBHOOK

class EvernoteWebhookHDL(request.RequestHandler):
    def get(self):
        miss_var = False
        params = {}

        if self.request.get('userId') and self.request.get('userId') != '':
    		params['user_id'] = self.request.get('userId')
    	else:
    		params['user_id'] = '[no userId]'
    		miss_var = True

    	if self.request.get('guid') and self.request.get('guid') != '':
    		params['guid'] = self.request.get('guid')
    	else:
    		params['guid'] = '[no guid]'
    		miss_var = True

    	if self.request.get('reason'):
    		if self.request.get('reason') == 'create' or self.request.get('reason') == 'update':
    			params['reason'] = self.request.get('reason')
    		else:
    			params['reason'] = '[wrong format reason: %s]' % self.request.get('reason')
	    		miss_var = True
    	else:
    		params['reason'] = '[no reason]'
    		miss_var = True

    	if miss_var:
            logging.warning('Evernote Webhook: %s %s %s' % (params['user_id'], params['guid'], params['reason']))
            return
    	else:
    		logging.debug('Evernote Webhook: %s %s %s' % (params['user_id'], params['guid'], params['reason']))

    	taskqueue.add(queue_name='sync-evernote', url='/sync/evernote/note', params=params, method='GET')

app = webapp2.WSGIApplication([
    routes.DomainRoute('<:(?i)(www\.%s|localhost)>'%HOST, [
        webapp2.Route('/hook/%s'%EN_WEBHOOK, handler='webhook.EvernoteWebhookHDL:get', name='evernote-webhook', methods=['GET'])
    ])
], debug=True, config=request.app_config)
