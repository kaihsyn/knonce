import sys
sys.path.append('./lib')

import webapp2
import logging
import request

from evernote.edam.error import EDAMUserException, EDAMSystemException, EDAMNotFoundException

from knonce.unit import Unit
from knonce.note import Note
from knonce import helper

class SyncENHDL(request.RequestHandler):
	def note(self):
		
		""" verify parameters """
		names = ['user_id', 'guid', 'reason']
		for name in names:
			if self.request.get(name) is None or self.request.get(name) == '':
				logging.error('Evernote: guid = %s, not enough parameters.') % self.request.get('guid')
				return

		""" get unit info """
		try:
			unit = Unit.query(Unity.user_id==int(self.request.get('user_id')), Unity.connected==True).fetch(1, projection['notebook_guid', 'token'])
		except ValueError:
			logging.error('Evernote: user_id = %s, wrong user_id format.') % self.request.get('user_id')
			return

		if unit is None:
			logging.error('Evernote: guid = %s, can\'t get unit.') % self.request.get('guid')
			return

		""" get note metadata """
		client = helper.get_evernote_client(token=unit.token)
		note_store = client.get_note_store()
		
		try:
			note = note_store.getNote(unit.token, self.request.get('guid'), False, False, False, False)
		except EDAMUserException, e:
			logging.error('Evernote: guid = %s, EDAMUser code: %s, parm: %s') % (self.request.get('guid'), str(e.errorCode), e.parameter)
		except EDAMNotFoundException, e:
			logging.error('Evernote: guid = %s, EDAMNotFound identifier: %s, key: %s') % (self.request.get('guid'), e.identifier, e.key)

		""" check if deleting """
		if note.deleted is not None:
			note_key = Note.query(Note.guid==self.request.get('guid')).fetch(1, key_only=True)
			note_key.delete()

		if self.request.get('reason') == 'create'
			""" check notebook """
			if note.notebookGuid != unit.notebook_guid:
				""" skip sync """
				return
			else:
				#TODO sync

		elif self.request.get('reason') == 'update'
			""" check if don't have this note and notebook is different """
			if note.notebookGuid != unit.notebook_guid:
				note_key = Note.query(Note.guid==self.request.get('guid')).fetch(1, key_only=True)
				
				if note_key is not None:
					note_key.delete()
					logging.info('Evernote: guid = %s, note deleted since moved to other notebook.') % self.request.get('guid')
					return
				else:
					""" skip sync """
					return
			else:
				#TODO update: handle if already have the note or not

		logging.info('Evernote: guid = %s, synced.') % self.request.get('guid')

app = webapp2.WSGIApplication([
	webapp2.Route('/sync/evernote/note', handler='sync.SyncENHDL:note', name='sync-evernote-note', methods=['GET'])
	], debug=True, config=request.app_config)