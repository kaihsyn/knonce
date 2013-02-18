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
    print "  * ", notebook.name

# get a list of note metadata
pageSize = 10
 
filter = NoteFilter(order=Types.NoteSortOrder.UPDATED)

spec = NotesMetadataResultSpec()
spec.includeTitle = True
spec.includeUpdated = True

notes_meta = note_store.findNotesMetadata(auth_token, filter, 0, pageSize, spec)

for note in notes_meta.notes:
	print ' '.join([str(note.title), '-', str(note.updated)])
