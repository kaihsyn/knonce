import re
from google.appengine.api import files


#parse en-media tag for an evernote
#need parameters for auth_token guid and note_store
def parse_enmedia(raw,auth_token,guid,note_store):
    #find all <en-media> attribute
    sub_medias = re.findall('<en-media(.*?)>',raw,re.M)
    for subm in sub_medias:
        split = re.split('[\' ="]',subm)
        if any("image/jpeg" in s for s in split) | any("image/gif" in s for s in split) | any("image/png" in s for s in split):
            hash_str = re.search('hash=["\'](.*?)["\']',subm)
            resource = note_store.getResourceByHash(auth_token,guid, hash_str.group(1).decode('hex'),True,False,False)
            file_name = files.blobstore.create(mime_type=resource.mime)
            with files.open(file_name, 'ab') as f:
                 f.write(resource.data.body)
            files.finalize(file_name)
            blob_key = files.blobstore.get_blob_key(file_name)
            raw = raw.replace('<en-media'+subm+'>','<img src="http://www.knonce.com/resource/XXX" width="123" height="123"/>')
        else:
            raw = raw.replace('<en-media'+subm+'>','')
            
    raw = raw.replace('</en-media(.*?)>','')
            
