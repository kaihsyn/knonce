import sys
sys.path.append('./lib')

import evernote.edam.type.ttypes as Types

from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter
from evernote.edam.notestore.ttypes import NotesMetadataResultSpec

# connect to evernote
auth_token = "S=s1:U=5d553:E=1443a0a7f01:C=13ce2595301:P=1cd:A=en-devtoken:H=c9ad0a0fb0de6969bb6ddb7a1815c084"
client = EvernoteClient(token=auth_token, sandbox=True)

# get notestore
note_store = client.get_note_store()

# list notebooks
notebooks = note_store.listNotebooks()
for notebook in notebooks:
    print "  * ", notebook.name, " - ", notebook.guid

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
	print ' - '.join([str(note.title), str(note.updated), str(note.guid)])
	unit = note_store.getNote(auth_token, note.guid, True, True, False, False)
	print unit.content
	print '=========='
