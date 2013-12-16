import time
import logging
import re

from google.appengine.api import files

""" lazy parse for content """
def parse_evernote(raw):
    start_time = time.time()

    """ replace xml declaration """
    raw = re.sub('^(<\?xml +)( *(version|encoding) *= *"[A-Za-z0-9-._]*")* *\?>\s*', '', raw, 1)

    """ replace doctype """
    raw = re.sub('^(<\!DOCTYPE +)[ A-Za-z0-9\."\-_:\/&=%]*>\s*', '', raw, 1)

    """ replace en-note """
    sub_match = re.findall('<en-note(.*?)>',raw,re.M|re.I)
    for en_sub in sub_match:
        split = re.split('[ =]',en_sub)
        temp_str = ""
        insert = False
        for s in split:
            if s != "":
                if insert:
                    insert = False
                    temp_str+="="+s
                elif s == 'title':
                    insert = True
                    temp_str+=" "+s
                elif s == 'style':
                    insert = True
                    temp_str+=" "+s
                elif s == 'lang':
                    insert = True
                    temp_str+=" "+s
                elif s == 'xml:lang':
                    insert = True
                    temp_str+=" "+s
        raw = raw.replace(en_sub,temp_str)
    raw = raw.replace('en-note','div')

    """ replace en-crypt """
    raw = re.sub('<en\-crypt( +((?!>).)*)* *>((?!(</en\-crypt *>)).)*</en\-crypt *>', '', raw)

    """ replace en-todo """
    raw = re.sub('<en\-todo( +checked *= *"false")? */>', '<i class="icon-check-empty"></i>', raw)
    raw = re.sub('<en\-todo( +checked *= *"false")? *></en-todo *>', '<i class="icon-check-empty"></i>', raw)

    raw = re.sub('<en\-todo +checked *= *"true" */>', '<i class="icon-check"></i>', raw)
    raw = re.sub('<en\-todo +checked *= *"true" *></en-todo *>', '<i class="icon-check"></i>', raw)

    """ replace en-media """
    raw = re.sub('<en\-media( +((?!>).)*)* */>', '', raw)
    raw = re.sub('<en\-media( +((?!>).)*)* *></en-media *>', '', raw)

    parsing_time = (time.time() - start_time) * 1000

    return [raw, parsing_time]

def create_summary(raw):

    """ remove all tags """
    raw = re.sub('<((?![<>]).)*>', '', raw)

    return raw[:280]

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
