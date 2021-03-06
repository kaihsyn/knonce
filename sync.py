import sys
sys.path.append('./lib')

import re
import urllib
import webapp2
import logging
import string
from google.appengine.ext import ndb
from webapp2_extras import routes
from secrets import HOST
import request
from evernote.edam.error.ttypes import EDAMErrorCode, EDAMUserException, EDAMSystemException, EDAMNotFoundException
from knonce.unit import Unit, UnitStatus
from knonce.note import Note
from knonce import helper
from knonce import parse

class SyncSettings:
	max_length = 3200

class SyncENHDL(request.RequestHandler):
	def note(self):
		
		""" verify parameters """
		names = ['user_id', 'guid', 'reason']
		for name in names:
			if self.request.get(name) is None or self.request.get(name) == '':
				logging.error('en-note-guid = %s, not enough parameters.' % self.request.get('guid'))
				return

		""" get unit info """
		try:
			unit_arr = Unit.query(Unit.user_id==int(self.request.get('user_id'))).fetch(1, projection=['notebook_guid', 'token', 'status'])
		except ValueError:
			logging.error('en-user-id = %s, wrong user_id format.' % self.request.get('user_id'))
			return

		if len(unit_arr) <= 0:
			logging.info('en-note-guid = %s, unit don\t exist in database.' % self.request.get('guid'))
			return

		unit = unit_arr[0]

		if unit.token is None or unit.token == '':
			logging.info('en-note-guid = %s, unit token is none.' % self.request.get('guid'))
			return

		if unit.status != UnitStatus.Active:
			logging.info('en-note-guid = %s, unit not active.' % self.request.get('guid'))
			return

		""" get note metadata """
		try:
			client = helper.get_evernote_client(token=unit.token)
			note_store = client.get_note_store()
			en_note = note_store.getNote(unit.token, self.request.get('guid'), False, False, False, False)
		except (EDAMUserException, EDAMSystemException) as e:
			return self.en_user_system_exception(unit, e, self.request.get('guid'))
		except EDAMNotFoundException as e:
			return self.en_not_found_exception(e, self.request.get('guid'))

		""" start sync """
		if self.request.get('reason') == 'create':

			""" check notebook """
			if en_note.notebookGuid != unit.notebook_guid:
				""" skip sync """
				logging.info('skipped: not in notebook')
				return

			""" check length """
			if en_note.contentLength > SyncSettings.max_length:
				""" skip sync """
				logging.info('skipped: length exceed limit, do not create note')
				return

			""" SYNC: create a new note """
			try:
				en_content = note_store.getNoteContent(unit.token, self.request.get('guid'))
			except (EDAMUserException, EDAMSystemException) as e:
				return self.en_user_system_exception(unit, e, self.request.get('guid'))
			except EDAMNotFoundException as e:
				return self.en_not_found_exception(e, self.request.get('guid'))

			self.make_note(None, unit, en_note, en_content)
			
			logging.info('en-note-guid = %s, created and synced.' % self.request.get('guid'))

		elif self.request.get('reason') == 'update':

			note = ndb.Key(flat=list(unit.key.flat())+['Note', 'en-%s' % en_note.guid]).get()

			if en_note.notebookGuid == unit.notebook_guid:

				if note is not None:

					if en_note.deleted is not None:
						""" deleted """
						note.key.delete()
						logging.info('en-note-guid = %s, deleted from notebook.' % self.request.get('guid'))
						return

					if en_note.contentLength > SyncSettings.max_length:
						""" check length """
						note.key.delete()
						logging.info('skipped: length exceed limit, delete current note')
						return

			else:

				if note is None:
					logging.info('note is none %s'%str(list(unit.key.flat())+['Note', 'en-%s'%en_note.guid]))
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
					""" moved to other notebook """
					note.key.delete()
					logging.warning('en-note-guid = %s, action cause note to be deleted.' % self.request.get('guid'))
					return

			try:
				en_content = note_store.getNoteContent(unit.token, self.request.get('guid'))
			except (EDAMUserException, EDAMSystemException) as e:
				return self.en_user_system_exception(unit, e, self.request.get('guid'))
			except EDAMNotFoundException as e:
				return self.en_not_found_exception(e, self.request.get('guid'))

			""" SYNC: check if the note is in database, if not, create one """
			add = False
			if note is None:
				add = True

			""" MAKE NOTE """
			self.make_note(note, unit, en_note, en_content)

			if add:
				logging.info('en-note-guid = %s, created and synced in update.' % self.request.get('guid'))
			else:
				logging.info('en-note-guid = %s, synced.' % self.request.get('guid'))

	@ndb.transactional(xg=True)
	def make_note(self, note, unit, en_note, en_content):
		if note is None:
			note = Note(id='en-%s'%en_note.guid, parent=unit.key)

		""" set note title """
		en_note.title = en_note.title #.decode('utf-8')

		if note.title != en_note.title:

			note.title = en_note.title

			""" handle english and non-english short name """
			if all(c in string.printable for c in en_note.title):
				short = '-'.join(re.findall('\w+', en_note.title)).lower()
			else:
				#short = urllib.quote(en_note.title.encode('utf-8')).lower()
				#short = re.sub('\W+', '-', en_note.title.encode('utf-8')).lower()
				short = re.sub('\s+', '-', en_note.title, flags=re.U).lower()

			""" if short name is too long or duplicated """
			retry = 0
			while len(short) > 450 or Note.query(Note.short==short, ancestor=unit.key).get() is not None:
				short = self.get_lazy_short_name(unit.key)
				retry += 1

				if retry >= 10:
					logging.error('en-note-guid = %s, faild to create lazy short name.' % en_note.guid)
					raise Exception

			note.short = short

		note.content = parse.parse_evernote(en_content)
		note.summary = parse.create_summary(note.content)
		note.usn = en_note.updateSequenceNum
		note.updated = en_note.updated
		note.created = en_note.created

		note.put()

	@ndb.transactional
	def get_lazy_short_name(self, unit_key):
		unit = unit_key.get()
		unit.name_count = unit.name_count + 1
		unit.put()

		return str(unit.name_count)

	def en_user_system_exception(self, unit, exception, guid=None):
		msg = ''

		if guid is not None:
			msg += 'en-note-guid = %s, ' % guid

		msg += 'EDAMUser code: %s %s, parm: %s' % (str(exception.errorCode), EDAMErrorCode._VALUES_TO_NAMES[exception.errorCode], exception.parameter)

		if exception.errorCode == EDAMErrorCode._NAMES_TO_VALUES['AUTH_EXPIRED']:
			unit = unit.key.get()
			unit.token = ''
			unit.put()
			logging.info(msg)
		else:
			logging.error(msg)

	def en_not_found_exception(self, exception, guid=None):
		msg = ''

		if guid is not None:
			msg += 'en-note-guid = %s, ' % guid

		msg += 'EDAMNotFound identifier: %s, key: %s' % (exception.identifier, exception.key)

		logging.error(msg)

app = webapp2.WSGIApplication([
	routes.DomainRoute('<:(?i)(www\.%s|localhost)>'%HOST, [
		webapp2.Route('/sync/evernote/note', handler='sync.SyncENHDL:note', name='sync-evernote-note', methods=['GET'])
	])
], debug=True, config=request.app_config)
