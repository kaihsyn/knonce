import logging
import re
import request
import string
import urllib
import webapp2

from evernote.api.client import EvernoteClient
from evernote.edam.error.ttypes import EDAMErrorCode, EDAMUserException, EDAMSystemException, EDAMNotFoundException
from google.appengine.ext import ndb
from knonce import helper
from knonce import parse
from knonce.contract import Contract
from knonce.note import Note
from knonce.unit import Unit, UnitStatus
from secrets import HOST, DEBUG
from webapp2_extras import routes

class SyncENHDL(request.RequestHandler):
    
    clent = None;
    note_store = None;

    def note(self):

        Contract.requires_not_none_or_empty(self.request.get('user_id'))
        Contract.requires_not_none_or_empty(self.request.get('guid'))
        Contract.requires_not_none_or_empty(self.request.get('reason'))

        unit = self.get_unit_by_en_user_id(self.request.get('user_id'))
        if unit is None:
            return

        self.client = EvernoteClient(token=unit.token, sandbox=False)
        self.note_store = self.client.get_note_store()

        en_note = self.get_en_note(unit.token, self.request.get('guid'))
        if en_note is None:
            return

        en_tags = self.get_en_tags(unit.token, self.request.get('guid'))

        note = None
        if self.request.get('reason') == 'update' or self.request.get('reason') == 'business_update':
            note = self.get_note(unit.key, self.request.get('guid'))

        if note is not None:
            if en_note.deleted is not None or not self.has_tag(en_tags):
                self.delete_note(note)
                logging.info('Note deleted: en_note_guid=%s' % self.request.get('guid'))
            else:
                parsing_time = self.sync_note(unit, note, en_note)
                logging.info('Note is synced. en-note-guid=%s parsing_time=%sms'%(self.request.get('guid'), parsing_time))
        
        else:
            if en_note.deleted is None and self.has_tag(en_tags):
                parsing_time = self.sync_note(unit, note, en_note)
                logging.info('Note is synced. en-note-guid=%s parsing_time=%sms'%(self.request.get('guid'), parsing_time))

    def get_unit_by_en_user_id(self, en_user_id):

        Contract.requires_not_none_or_empty(en_user_id)

        try:
            unit_list = Unit.query(Unit.user_id==int(en_user_id)).fetch(1, projection=['token'])

        except ValueError:
            logging.error('Wrong user_id format: %s'%en_user_id)
            return None

        if len(unit_list) <= 0:
            logging.info('User doesn\'t exist in datastore: %s'%en_user_id)
            return None

        unit = unit_list[0]
        if unit.token is None or unit.token == '':
            logging.info('Unit token is none: %s'%en_user_id)
            return None

        return unit

    def get_en_note(self, en_token, en_guid):

        Contract.requires_not_none(self.note_store)

        en_note = None

        try:
            en_note = self.note_store.getNote(en_token, en_guid, False, False, False, False)
        except (EDAMUserException, EDAMSystemException) as e:
            self.en_user_system_exception(unit.key, e, self.request.get('guid'))
        except EDAMNotFoundException as e:
            self.en_not_found_exception(e, self.request.get('guid'))

        return en_note

    def get_en_tags(self, en_token, en_guid):

        Contract.requires_not_none(self.note_store)

        try:
            en_tags = self.note_store.getNoteTagNames(en_token, en_guid)
        except (EDAMUserException, EDAMSystemException) as e:
            self.en_user_system_exception(unit.key, e, self.request.get('guid'))
        except EDAMNotFoundException as e:
            self.en_not_found_exception(e, self.request.get('guid'))

        if en_tags == None:
            en_tags = []

        return en_tags

    def get_note(self, unit_key, en_guid):

        return ndb.Key(flat=list(unit_key.flat())+['Note', 'en-%s'%en_guid]).get()

    def has_tag(self, en_tags):

        tags = []
        for tag in en_tags:
            tags = tags + [tag.lower()]

        return ('mxchar' in tags)

    def delete_note(self, note):

        if note is not None:
            note.key.delete()
        return

    def sync_note(self, unit, note, en_note):

        if note is None:
            """ create new note """
            note = Note(id='en-%s'%en_note.guid, parent=unit.key)

        en_content = self.get_en_content(unit.token, en_note.guid)

        if en_content is None:
            logging.warning('Note content is None: en_note_guid=%s'%en_note.guid)

        note, parsing_time = self.update_note(unit.key, note, en_note, en_content)
        note.put()

        return parsing_time

    def get_en_content(self, en_token, en_note_guid):

        Contract.requires_not_none(self.note_store)

        en_content = None

        try:
            en_content = self.note_store.getNoteContent(en_token, en_note_guid)
        except (EDAMUserException, EDAMSystemException) as e:
            self.en_user_system_exception(note_key, e, en_note_guid)
        except EDAMNotFoundException as e:
            self.en_not_found_exception(e, en_note_guid)
        
        return en_content

    @ndb.transactional(xg=True)
    def update_note(self, unit_key, note, en_note, en_content):

        Contract.requires_not_none(unit_key)
        Contract.requires_not_none(note)
        Contract.requires_not_none(en_note)
        Contract.requires_not_none(en_content)

        """ parse content """
        parsed_content, parsing_time = parse.parse_evernote(en_content)

        """ update fields """
        if note.title != en_note.title:
            note.short = self.create_shortname(unit_key, en_note.title)

        note.title   = en_note.title
        note.usn     = en_note.updateSequenceNum
        note.updated = en_note.updated
        note.created = en_note.created
        note.content = parsed_content

        Contract.ensures_not_none_or_empty(note.short)

        return [note, parsing_time]

    def create_shortname(self, unit_key, note_title):

        """ handle english and non-english short name """
        if all((char in string.printable) for char in note_title):
            short = '-'.join(re.findall('\w+', note_title)).lower()
        else:
            short = re.sub('\s+', '-', note_title, flags=re.U).lower()

        """ if short name is too long or duplicated """
        retry = 0
        while len(short) > 450 or Note.query(Note.short==short, ancestor=unit_key).get() is not None:
            short = self.get_lazy_short_name(unit_key)
            retry += 1

            if retry >= 10:
                logging.error('en-note-guid = %s, faild to create lazy short name.'%en_note.guid)
                raise Exception

        return short


    @ndb.transactional
    def get_lazy_short_name(self, unit_key):
        unit = unit_key.get()
        unit.name_count = unit.name_count + 1
        unit.put()

        return str(unit.name_count)
    
    def en_user_system_exception(self, unit_key, exception, guid=None):
        msg = ''

        if guid is not None:
            msg += 'en-note-guid = %s, '%guid

        msg += 'EDAMUser code: %s %s, parm: %s'%(str(exception.errorCode), EDAMErrorCode._VALUES_TO_NAMES[exception.errorCode], exception.parameter)

        if exception.errorCode == EDAMErrorCode._NAMES_TO_VALUES['AUTH_EXPIRED']:
            unit = unit_key.get()
            unit.token = None
            unit.put()
            logging.info(msg)
        else:
            logging.error(msg)

    def en_not_found_exception(self, exception, guid=None):
        msg = ''

        if guid is not None:
            msg += 'en-note-guid = %s, '%guid

        msg += 'EDAMNotFound identifier: %s, key: %s'%(exception.identifier, exception.key)

        logging.error(msg)

app = webapp2.WSGIApplication([
    routes.DomainRoute('<:(?i)(www\.%s|localhost)>'%HOST, [
        webapp2.Route('/sync/evernote/note', handler='sync.SyncENHDL:note', name='sync-evernote-note', methods=['GET'])
    ])
], debug=DEBUG, config=request.app_config)
