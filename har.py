#!/usr/bin/python3

import hashlib
import json
import os
import base64
from urllib.parse import urlparse

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
      if self.filename.endswith("%s.har"%(urlhash) ):
        self.baseurl = urlparse(url).netloc
        self.basehash = urlhash

  def load_har(self, filename):
    self.filename = filename
    with open(filename) as f:
      self.hardata = json.loads( f.read() )
    self.get_baseurl()
    self.extract_files_from_har()
    self.rewrite_paths_in_html()

  def extract_files_from_har(self):
    for entry in self.hardata['log']['entries']:
      url     = entry['request']['url']
      m       = hashlib.sha1()
      m.update(url.encode())
      urlhash = m.hexdigest()
      self.urlhashes[urlhash] = {'url': url, 'extension': ''}
      filemode = 'w'
      if entry['response']['content']['mimeType'].startswith( 'text/html' ):
        self.urlhashes[urlhash]['extension'] = 'html'
        content = entry['response']['content']['text']
      elif entry['response']['content']['mimeType'] == 'application/json':
        self.urlhashes[urlhash]['extension'] = 'json'
        content = entry['response']['content']['text']
      elif entry['response']['content']['mimeType'] == 'text/plain':
        self.urlhashes[urlhash]['extension'] = 'txt'
        content = entry['response']['content']['text']
      elif entry['response']['content']['mimeType'] == 'application/octet-stream':
        self.urlhashes[urlhash]['extension'] = 'txt'
        content = entry['response']['content']['text']
      elif entry['response']['content']['mimeType'].startswith( 'text/css' ):
        self.urlhashes[urlhash]['extension'] = 'css'
        content = entry['response']['content']['text']
      elif entry['response']['content']['mimeType'].startswith( 'application/javascript' ):
        self.urlhashes[urlhash]['extension'] = 'js'
        content = entry['response']['content']['text']
      elif entry['response']['content']['mimeType'].startswith( 'image/svg' ):
        self.urlhashes[urlhash]['extension'] = 'svg'
        content = entry['response']['content']['text']
      elif entry['response']['content']['mimeType'].startswith( 'image/png' ):
        filemode = 'wb'
        self.urlhashes[urlhash]['extension'] = 'png'
        content = base64.b64decode( entry['response']['content']['text'] )
      elif entry['response']['content']['mimeType'].startswith( 'image/jpg' ):
        filemode = 'wb'
        self.urlhashes[urlhash]['extension'] = 'jpg'
        content = base64.b64decode( entry['response']['content']['text'] )
      else:
        continue

      with open(os.path.join('temp', '%s.%s'%(urlhash, self.urlhashes[urlhash]['extension'])), filemode) as f:
        f.write(content)

  def rewrite_paths_in_html(self):
    for file in os.listdir('temp'):
      if file.endswith('.html'):
        #print(file)  # printing file name of desired extension
        with open(os.path.join( 'temp', file) ) as f:
          data = f.read()

        for hash in self.urlhashes:
          #print(self.urlhashes[hash]['url'])
          if self.urlhashes[hash]['url'] in data:
            #print("Replacing %s with %s"%(self.urlhashes[hash]['url'], "%s.%s"%(hash, self.urlhashes[hash]['extension']) ) )
            data = data.replace(self.urlhashes[hash]['url'], "%s.%s"%(hash, self.urlhashes[hash]['extension']))

          #Now do the same for relative links
          urlcomp = urlparse(self.urlhashes[hash]['url'])
          #print(urlcomp)
          relurl = "%s%s%s%s%s" %(urlcomp.path, '?' if urlcomp.fragment else '', urlcomp.query, '#' if urlcomp.fragment else '', urlcomp.fragment)
          #print(relurl)
          if urlcomp.netloc == self.baseurl and relurl in data:
            print("Replacing %s with %s"%(relurl, "%s.%s"%(hash, self.urlhashes[hash]['extension']) ) )
            data = data.replace(relurl, "%s.%s"%(hash, self.urlhashes[hash]['extension']))

        #print("Removing all cross origin and integrity attributes from tags...")
        data = data.replace("crossorigin=\"anonymous\"", "")
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

