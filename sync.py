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
				logging.error('en-note-guid = %s, not enough parameters.') % self.request.get('guid')
				return

		""" get unit info """
		try:
			unit = Unit.query(Unity.user_id==int(self.request.get('user_id')), Unity.connected==True).fetch(1, projection['notebook_guid', 'token'])
		except ValueError:
			logging.error('en-user-id = %s, wrong user_id format.') % self.request.get('user_id')
			return
		if unit is None:
			logging.error('en-note-guid = %s, can\'t get unit.') % self.request.get('guid')
			return

		""" get note metadata """
		client = helper.get_evernote_client(token=unit.token)
		note_store = client.get_note_store()
		
		try:
			en_note = note_store.getNote(unit.token, self.request.get('guid'), False, False, False, False)
		except EDAMUserException, e:
			logging.error('en-note-guid = %s, EDAMUser code: %s, parm: %s') % (self.request.get('guid'), str(e.errorCode), e.parameter)
		except EDAMNotFoundException, e:
			logging.error('en-note-guid = %s, EDAMNotFound identifier: %s, key: %s') % (self.request.get('guid'), e.identifier, e.key)

		""" start sync """
		if self.request.get('reason') == 'create':

			""" check notebook """
			if en_note.notebookGuid != unit.notebook_guid:

				""" skip sync """
				return

			else:

				""" SYNC: create a new note """
				try:
					en_note = note_store.getNote(unit.token, self.request.get('guid'), True, False, False, False)
				except EDAMUserException, e:
					logging.error('en-note-guid = %s, EDAMUser code: %s, parm: %s') % (self.request.get('guid'), str(e.errorCode), e.parameter)
				except EDAMNotFoundException, e:
					logging.error('en-note-guid = %s, EDAMNotFound identifier: %s, key: %s') % (self.request.get('guid'), e.identifier, e.key)

				note = Note(id='en-%s' % en_note.guid, parent=unit.key)

				note.usn = en_note.updateSequenceNum
				note.title = en_note.title
				note.content = parse.parse_evernote(en_note.content)
				note.updated = en_note.updated
				note.created = en_note.created

				note.put()
				logging.info('en-note-guid = %s, created and synced.') % self.request.get('guid')

		elif self.request.get('reason') == 'update':

			if en_note.notebookGuid == unit.notebook_guid:

				""" SYNC: check if the note is in database, if not, create one """
				note = ndb.Key(flat=list(unit.key.pairs()).append(('Note', 'en-%s' % en_note.guid))).get()
				
				if note is None:
					note = Note(id='en-%s' % en_note.guid, parent=unit.key)

				note.usn = en_note.updateSequenceNum
				note.title = en_note.title
				note.content = parse.parse_evernote(en_note.content)
				note.updated = en_note.updated
				note.created = en_note.created

				note.put()
				logging.info('en-note-guid = %s, synced.') % self.request.get('guid')

			else:

				note = ndb.Key(flat=list(unit.key.pairs()).append(('Note', 'en-%s' % en_note.guid))).get()

				if note is None:

					return

				else:

					if en_note.deleted is not None:

						""" deleted """
						note.key.delete()
						logging.info('en-note-guid = %s, deleted from notebook.') % self.request.get('guid')
						return

					elif en_note.notebookGuid != unit.notebook_guid:

						""" moved to other notebook """
						note.key.delete()
						logging.info('en-note-guid = %s, delete note since moved out of notebook.') % self.request.get('guid')
						return

					else:

						return

app = webapp2.WSGIApplication([
	webapp2.Route('/sync/evernote/note', handler='sync.SyncENHDL:note', name='sync-evernote-note', methods=['GET'])
	], debug=True, config=request.app_config)