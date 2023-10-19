#!/usr/bin/python3

import hashlib
import json
import os
import base64
from urllib.parse import urlparse
from gzip import GzipFile
import re

class Har:
  def __init__(self):
    os.makedirs( 'temp', exist_ok=True )
    self.urlhashes = {}
    self.hardata = None
    self.filename = None
    self.baseurl  = None
    self.basehash = None

  def get_baseurl(self):
    for entry in self.hardata['log']['entries']:
      url       = entry['request']['url']
      m         = hashlib.sha1()
      m.update(url.encode())
      urlhash   = m.hexdigest()
      if self.filename.endswith("%s.har"%(urlhash) ) or self.filename.endswith("%s.har.gz"%(urlhash) ):
        self.baseurl = urlparse(url).netloc
        self.basehash = urlhash

  def load_har(self, filename):
    self.filename = filename
    if filename.endswith('.har'):
      with open(filename) as f:
        self.hardata = json.loads( f.read() )
    elif filename.endswith('.gz'):
      with open(filename, 'rb') as f:
        self.hardata = json.loads( GzipFile(mode='r', fileobj=f).read() )
    else:
      return
    self.get_baseurl()
    self.extract_files_from_har()
    self.rewrite_paths_in_html()

  def extract_files_from_har(self):
    print(self.basehash)
    for entry in self.hardata['log']['entries']:
      url     = entry['request']['url']
      m       = hashlib.sha1()
      m.update(url.encode())
      urlhash = m.hexdigest()
      self.urlhashes[urlhash] = {'url': url, 'extension': ''}
      filemode = 'w'
      mimetype = entry['response']['content']['mimeType']
      if mimetype.startswith( 'text/html' ):
        self.urlhashes[urlhash]['extension'] = 'html'
        content = entry['response']['content']['text']
      elif mimetype == 'application/json':
        self.urlhashes[urlhash]['extension'] = 'json'
        content = entry['response']['content']['text']
      elif mimetype == 'text/plain':
        self.urlhashes[urlhash]['extension'] = 'txt'
        content = entry['response']['content']['text']
      elif mimetype == 'application/octet-stream':
        self.urlhashes[urlhash]['extension'] = 'txt'
        content = entry['response']['content']['text']
      elif mimetype.startswith( 'text/css' ):
        self.urlhashes[urlhash]['extension'] = 'css'
        content = entry['response']['content']['text']
      elif mimetype.startswith( 'application/javascript' ):
        self.urlhashes[urlhash]['extension'] = 'js'
        content = entry['response']['content']['text']
      elif mimetype.startswith( 'image/svg' ):
        self.urlhashes[urlhash]['extension'] = 'svg'
        content = entry['response']['content']['text']
      elif mimetype.startswith( 'font/woff2' ):
        filemode = 'wb'
        self.urlhashes[urlhash]['extension'] = 'woff2'
        content = base64.b64decode( entry['response']['content']['text'] )
      elif mimetype.startswith( 'image/png' ):
        filemode = 'wb'
        self.urlhashes[urlhash]['extension'] = 'png'
        content = base64.b64decode( entry['response']['content']['text'] )
      elif mimetype.startswith( 'image/jpg' ) or mimetype.startswith( 'image/jpeg' ):
        filemode = 'wb'
        self.urlhashes[urlhash]['extension'] = 'jpg'
        content = base64.b64decode( entry['response']['content']['text'] )
      elif mimetype == '':
        if '.jpg' in entry['request']['url'] or '.jpeg' in entry['request']['url']:
            filemode = 'wb'
            self.urlhashes[urlhash]['extension'] = 'jpg'
            content = base64.b64decode( entry['response']['content']['text'] )
      else:
        continue

      #print('Writing: %s.%s %s'%(urlhash, self.urlhashes[urlhash]['extension'], url))
      with open(os.path.join('temp', '%s.%s'%(urlhash, self.urlhashes[urlhash]['extension'])), filemode) as f:
        f.write(content)

  def rewrite_paths_in_html(self):
    for file in os.listdir('temp'):
      if file.endswith('.html'):
        #print(file)  # printing file name of desired extension
        with open(os.path.join( 'temp', file) ) as f:
          data = f.read().replace('&amp;', '&')

        for hash in self.urlhashes:
          #print(self.urlhashes[hash]['url'])
          if self.urlhashes[hash]['url'] in data:
            #print("Replacing %64s with %s"%(self.urlhashes[hash]['url'], "%s.%s"%(hash, self.urlhashes[hash]['extension']) ) )
            data = data.replace(self.urlhashes[hash]['url'], "%s.%s"%(hash, self.urlhashes[hash]['extension']))
            #data = re.sub(self.urlhashes[hash]['url'], "%s.%s"%(hash, self.urlhashes[hash]['extension']), data)

          #Now do the same for relative links
          urlcomp = urlparse(self.urlhashes[hash]['url'])
          relurl = "%s%s%s%s%s" %(urlcomp.path, '?' if urlcomp.query else '', urlcomp.query, '#' if urlcomp.fragment else '', urlcomp.fragment)
          if relurl in data and relurl != '/':
            #print("Replacing %64s with %s"%(relurl, "%s.%s"%(hash, self.urlhashes[hash]['extension']) ) )
            data = data.replace(relurl, "%s.%s"%(hash, self.urlhashes[hash]['extension']))
            #data = re.sub(relurl, "%s.%s"%(hash, self.urlhashes[hash]['extension']), data)

        #print("Removing all cross origin and integrity attributes from tags...")
        data = re.sub(r"crossorigin=\"anonymous\"", "", data)
        #data = re.sub(r"integrity=\"[a-zA-Z0-9\-\+\/\=]+\"", "", data)
        data = data.replace("integrity=\"[^\"]+\"", "")
        
        #print("Now writing to: %s"%( os.path.join( 'kanweg', file) ) )
        with open(os.path.join( 'temp', file), 'w') as f:
          f.write(data)

#print(self.urlhashes)
if __name__ == '__main__':
  har = Har()
  har.load_har('git/99e82a53e74e05c86bce979f2f0f6468842f7b80.har')
  print(har.baseurl)
  print(har.basehash)

