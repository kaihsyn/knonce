import evernote.api.client.EvernoteClient as EvernoteClient
import logging
import re
import request
import string
import urllib
import webapp2

from evernote.edam.error.ttypes import EDAMErrorCode, EDAMUserException, EDAMSystemException, EDAMNotFoundException
from google.appengine.ext import ndb
from knonce import helper
from knonce import parse
from knonce.contract import Contract
from knonce.note import Note
from knonce.unit import Unit, UnitStatus
from secrets import HOST
from webapp2_extras import routes

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
			unit_arr = Unit.query(Unit.user_id==int(self.request.get('user_id'))).fetch(1, projection=['token'])
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

		""" get note metadata """
		try:
			client = EvernoteClient(token=unit.token, sandbox=False)
			note_store = client.get_note_store()
			en_note = note_store.getNote(unit.token, self.request.get('guid'), False, False, False, False)
		except (EDAMUserException, EDAMSystemException) as e:
			return self.en_user_system_exception(unit, e, self.request.get('guid'))
		except EDAMNotFoundException as e:
			return self.en_not_found_exception(e, self.request.get('guid'))

		""" get note entity """
		note = None
		if self.request.get('reason') == 'update' or self.request.get('business_update'):

			note = ndb.Key(flat=list(unit.key.flat())+['Note', 'en-%s' % en_note.guid]).get()

		""" check if note is deleted """
		if en_note.deleted is not None and note is not None:
			""" deleted """
			note.key.delete()
			logging.info('en-note-guid = %s, deleted from notebook.' % self.request.get('guid'))
			return

		""" create a new note is it doesn't exist in datastore """
		if note is None:
			""" create new note """
			note = Note(id='en-%s'%en_note.guid, parent=unit.key)
			logging.info('note is none %s'%str(list(unit.key.flat())+['Note', 'en-%s'%en_note.guid]))

		""" sync note content """
		try:
			en_content = note_store.getNoteContent(unit.token, self.request.get('guid'))
		except (EDAMUserException, EDAMSystemException) as e:
			return self.en_user_system_exception(unit, e, self.request.get('guid'))
		except EDAMNotFoundException as e:
			return self.en_not_found_exception(e, self.request.get('guid'))

		self.make_note(note, unit, en_note, en_content)
		logging.info('en-note-guid = %s, synced.' % self.request.get('guid'))

	@ndb.transactional(xg=True)
	def make_note(self, note, unit, en_note, en_content):

		Contract.requires_not_none(note)
		Contract.requires_not_none(unit)
		Contract.requires_not_none(en_note)
		Contract.requires_not_none(en_content)

		note.title = en_note.title
		note.content = parse.parse_evernote(en_content)
		note.summary = parse.create_summary(note.content)
		note.usn = en_note.updateSequenceNum
		note.updated = en_note.updated
		note.created = en_note.created

		if note.title != en_note.title:
			note.short = create_shortname(en_note.title)

		note.put()

	@ndb.transactional
	def get_lazy_short_name(self, unit_key):
		unit = unit_key.get()
		unit.name_count = unit.name_count + 1
		unit.put()

		return str(unit.name_count)

	def create_shortname(self, note_title):

		""" handle english and non-english short name """
		if all(c in string.printable for c in note_title):
			short = '-'.join(re.findall('\w+', note_title)).lower()
		else:
			short = re.sub('\s+', '-', note_title, flags=re.U).lower()

		""" if short name is too long or duplicated """
		retry = 0
		while len(short) > 450 or Note.query(Note.short==short, ancestor=unit.key).get() is not None:
			short = self.get_lazy_short_name(unit.key)
			retry += 1

			if retry >= 10:
				logging.error('en-note-guid = %s, faild to create lazy short name.' % en_note.guid)
				raise Exception

		return short

	def en_user_system_exception(self, unit, exception, guid=None):
		msg = ''

		if guid is not None:
			msg += 'en-note-guid = %s, ' % guid

		msg += 'EDAMUser code: %s %s, parm: %s' % (str(exception.errorCode), EDAMErrorCode._VALUES_TO_NAMES[exception.errorCode], exception.parameter)

		if exception.errorCode == EDAMErrorCode._NAMES_TO_VALUES['AUTH_EXPIRED']:
			unit = unit.key.get()
			unit.token = None
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
	#TODO remove knonce.com
	routes.DomainRoute('<:(?i)(www\.knonce\.com|www\.%s|localhost)>'%HOST, [
		webapp2.Route('/sync/evernote/note', handler='sync.SyncENHDL:note', name='sync-evernote-note', methods=['GET'])
	])
], debug=True, config=request.app_config)
