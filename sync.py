import sys
sys.path.append('./lib')

import webapp2
import logging

from google.appengine.ext import ndb

import request

from evernote.edam.error.ttypes import EDAMErrorCode, EDAMUserException, EDAMSystemException, EDAMNotFoundException

from knonce.unit import Unit
from knonce.note import Note
from knonce import helper
from knonce import parse

class SyncENHDL(request.RequestHandler):
	def note(self):
		
		""" verify parameters """
		names = ['user_id', 'guid', 'reason']
		for name in names:
			if self.request.get(name) is None or self.request.get(name) == '':
				logging.error('en-note-guid = %s, not enough parameters.' % self.request.get('guid'))
				return

		logging.info('LV1')

		""" get unit info """
		try:
			unit_arr = Unit.query(Unit.user_id==int(self.request.get('user_id')), Unit.token!='').fetch(1, projection=['notebook_guid', 'token'])
		except ValueError:
			logging.error('en-user-id = %s, wrong user_id format.' % self.request.get('user_id'))
			return
		if len(unit_arr) <= 0:
			logging.error('en-note-guid = %s, unit don\t exist in database.' % self.request.get('guid'))
			return

		logging.info('LV2')

		unit = unit_arr[0]

		""" get note metadata """
		try:
			client = helper.get_evernote_client(token=unit.token)
			note_store = client.get_note_store()
			en_note = note_store.getNote(unit.token, self.request.get('guid'), False, False, False, False)
		except EDAMUserException, e:
			if e.errorCode == EDAMErrorCode._NAMES_TO_VALUES['AUTH_EXPIRED']:
				unit = unit.key.get()
				unit.token = ''
				unit.put()
			logging.error('en-note-guid = %s, EDAMUser code: %s %s, parm: %s' % (self.request.get('guid'), str(e.errorCode), EDAMErrorCode._VALUES_TO_NAMES[e.errorCode], e.parameter))

		except EDAMNotFoundException, e:
			logging.error('en-note-guid = %s, EDAMNotFound identifier: %s, key: %s' % (self.request.get('guid'), e.identifier, e.key))

		""" start sync """
		if self.request.get('reason') == 'create':

			""" check notebook """
			if en_note.notebookGuid != unit.notebook_guid:
				""" skip sync """
				return

			""" SYNC: create a new note """
			try:
				en_note = note_store.getNote(unit.token, self.request.get('guid'), True, False, False, False)
			except EDAMUserException, e:
				logging.error('en-note-guid = %s, EDAMUser code: %s %s, parm: %s' % (self.request.get('guid'), str(e.errorCode), EDAMErrorCode._VALUES_TO_NAMES[e.errorCode], e.parameter))
			except EDAMNotFoundException, e:
				logging.error('en-note-guid = %s, EDAMNotFound identifier: %s, key: %s' % (self.request.get('guid'), e.identifier, e.key))

			note = Note(id='en-%s' % en_note.guid, parent=unit.key)

			note.usn = en_note.updateSequenceNum
			note.title = en_note.title
			note.content = parse.parse_evernote(en_note.content)
			note.updated = en_note.updated
			note.created = en_note.created

			note.put()
			logging.info('en-note-guid = %s, created and synced.' % self.request.get('guid'))

		elif self.request.get('reason') == 'update':

			note = ndb.Key(flat=list(unit.key.flat())+['Note', 'en-%s' % en_note.guid]).get()

			if en_note.notebookGuid == unit.notebook_guid:

				if note is None:
					return

				if en_note.deleted is not None:
					""" deleted """
					note.key.delete()
					logging.info('en-note-guid = %s, deleted from notebook.' % self.request.get('guid'))
					return

			else:

				if note is None:
					return

				if en_note.deleted is not None:
					""" deleted """
					note.key.delete()
					logging.info('en-note-guid = %s, deleted from notebook.' % self.request.get('guid'))
					return

				elif en_note.notebookGuid != unit.notebook_guid:
					""" moved to other notebook """
					note.key.delete()
					logging.info('en-note-guid = %s, delete note since moved out of notebook.' % self.request.get('guid'))
					return

				else:
					return

			""" SYNC: check if the note is in database, if not, create one """
			if note is None:
				note = Note(id='en-%s' % en_note.guid, parent=unit.key)

			note.usn = en_note.updateSequenceNum
			note.title = en_note.title
			note.content = parse.parse_evernote(en_note.content)
			note.updated = en_note.updated
			note.created = en_note.created

			note.put()
			logging.info('en-note-guid = %s, synced.' % self.request.get('guid'))

app = webapp2.WSGIApplication([
	webapp2.Route('/sync/evernote/note', handler='sync.SyncENHDL:note', name='sync-evernote-note', methods=['GET'])
	], debug=True, config=request.app_config)
