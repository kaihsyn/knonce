from __future__ import with_statement

import logging
from google.appengine.api import files

import sys
sys.path.append('./lib')

import evernote.edam.type.ttypes as Types

from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter
from evernote.edam.notestore.ttypes import NotesMetadataResultSpec

def sandbox():
	# connect to evernote
	auth_token = "S=s1:U=5d553:E=14501517f86:C=13da9a05386:P=1cd:A=en-devtoken:V=2:H=efe4a8b4effc55003bac87158cdd6f87"
	client = EvernoteClient(token=auth_token, sandbox=True)

	# get notestore
	note_store = client.get_note_store()

	# list notebooks
	notebooks = note_store.listNotebooks()
	for notebook in notebooks:
	    logging.info("  * ", notebook.name, " - ", notebook.guid)

	# get a list of note metadata
	pageSize = 10
	 
	filter = NoteFilter(order=Types.NoteSortOrder.UPDATED, notebookGuid=notebooks[0].guid)

	spec = NotesMetadataResultSpec()
	spec.includeGuid = True
	spec.includeTitle = True
	spec.includeContent = True
	spec.includeUpdated = True

	notes_meta = note_store.findNotesMetadata(auth_token, filter, 0, pageSize, spec)

	#note_list = note_store.findNotes(auth_token, filter, 0, 10)

	for note in notes_meta.notes:
		logging.info(' - '.join([str(note.title), str(note.updated), str(note.guid)]))
		unit = note_store.getNote(auth_token, note.guid, True, True, False, False)
		logging.info(unit.content)

		for resource in unit.resources:
			file_name = files.blobstore.create(mime_type=resource.mime)
			with files.open(file_name, 'a') as f:
			  f.write(resource.data.body)
			files.finalize(file_name)
			blob_key = files.blobstore.get_blob_key(file_name)

			logging.info(blob_key)

		logging.info('==========')

