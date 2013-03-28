import sys
sys.path.append('./lib')

import webapp2
import logging

#from knonce.model.unit import Unit
#from evernote.api.client import EvernoteClient
#import evernote.edam.notestore.NoteStore as NoteStore

class SyncEvernoteHDL(webapp2.RequestHandler):
	def post(self):
		
		logging.info('Sync Evernote')

		"""
		# get unit info
		unit = Unit.query().get()

		# connect to evernote
		client = EvernoteClient(token=unit.evernote_token, sandbox=True)

		# get notestore
		note_store = client.get_note_store()

		# list notebooks
		notebooks = note_store.listNotebooks()
		for notebook in notebooks:
			logging.info(notebook.name)
		"""

app = webapp2.WSGIApplication([
  ('/sync/evernote', SyncEvernoteHDL)
])