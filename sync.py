import sys
sys.path.append('./lib')

import webapp2
import logging

from knonce.model.unit import Unit
from evernote.api.client import EvernoteClient
import evernote.edam.notestore.NoteStore as NoteStore

class SyncHDL(webapp2.RequestHandler):
	def get(self):
		
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

app = webapp2.WSGIApplication([
  ('/sync', SyncHDL)
])