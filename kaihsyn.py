from __future__ import with_statement

import sys
sys.path.append('lib')

import evernote.edam.type.ttypes as Types

from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter
from evernote.edam.notestore.ttypes import NotesMetadataResultSpec

def sandbox():
	# connect to evernote
	auth_token = "S=s1:U=5d553:E=14558b4a895:C=13e01037c97:P=1cd:A=en-devtoken:V=2:H=fc42f231c2ddc95d86848b50cba94d9a"
	client = EvernoteClient(token=auth_token, sandbox=True)

	user_store = client.get_user_store()
	user = user_store.getUser()

	print "%s - %s" % (user.username, str(user.id))

	# get notestore
	note_store = client.get_note_store()

	# list notebooks
	notebooks = note_store.listNotebooks()
	for notebook in notebooks:
	    print "  * ", notebook.name, " - ", notebook.guid, " - ", notebook.updateSequenceNum

	# get a list of note metadata
	pageSize = 10
	
	for nbguid in notebooks:
		filter = NoteFilter(order=Types.NoteSortOrder.UPDATED, notebookGuid=nbguid.guid)

		spec = NotesMetadataResultSpec()
		spec.includeGuid = True
		spec.includeTitle = True
		spec.includeContent = True
		spec.includeUpdated = True
		spec.includeUpdateSequenceNum = True

		notes_meta = note_store.findNotesMetadata(auth_token, filter, 0, pageSize, spec)

		#note_list = note_store.findNotes(auth_token, filter, 0, 10)
		print '==============='
		for note in notes_meta.notes:
			print ' - '.join([str(note.title), str(note.updated), str(note.guid), str(note.updateSequenceNum)])
			"""
			unit = note_store.getNote(auth_token, note.guid, True, True, False, False)
			print unit.contentnfo('==========')
			"""

sandbox()
