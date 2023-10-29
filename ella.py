#!/usr/bin/python3

from git import Repo
from git import Git
import os, sys, shutil
import hashlib
from datetime import datetime
from urllib.parse import urlparse
import json
import re
import requests
from config import Config
import gzip
from spn2 import SPN2
from browser import Browser

config = Config()
spn2 = SPN2(access_key=config.config_object['SPN2']['access_key'], secret_key=config.config_object['SPN2']['secret_key'])
pdfregex = r"([^\'\"]+\.pdf)"
ssh_cmd = 'ssh -o StrictHostKeyChecking=accept-new -i %s' % os.path.join(os.getcwd(),'github', 'ella')
with open( os.path.join(os.getcwd(),'github', 'ella') , 'w') as f:
  f.write(config.config_object['GIT']['key']+"\n")
os.chmod(os.path.join(os.getcwd(),'github', 'ella'), 0o600)

if os.path.isdir( config.config_object['GIT']['dir'] ):
  print("repo exists in %s, pulling..."%(config.config_object['GIT']['dir']))
  repo = Repo( config.config_object['GIT']['dir'] )
  repo.git.update_environment(GIT_SSH_COMMAND=ssh_cmd)
  repo.remotes.origin.pull()
else:
  os.makedirs( config.config_object['GIT']['dir'], exist_ok=True )
  print("Cloning %s into %s"%(config.config_object['GIT']['url'], config.config_object['GIT']['dir']))
  repo = Repo.clone_from(config.config_object['GIT']['url'], 
                         os.path.join(os.getcwd(), 'git'),
                         env=dict(GIT_SSH_COMMAND=ssh_cmd))

urls = []
with open('urls.csv', 'r') as f:
  lines = f.readlines()
  
  for line in lines:
    if line != '' and not line.startswith('#'):
      urls.append(line.strip())

commit_files = [os.path.join(os.getcwd(), 'git', 'index.csv')]
urlhashes = {}
with open(os.path.join(os.getcwd(), 'git', 'index.csv'), 'r') as f:
  lines = f.readlines()
  for line in lines:
    if line.startswith('hash;'):
      continue
    try:
      h,u = line.split(';')
      urlhashes[h] = u.strip()
    except:
      pass

for url in urls:
  m = hashlib.sha1()
  browser = Browser()
  print("Getting url %s"%(url))
  if config.config_object['SPN2']['enabled']:
    spn2.submit(url)

  browser.get(url)
  m.update(url.encode())
  urlhash   = m.hexdigest()
  urlbase   = urlparse(url).netloc
  urlscheme = urlparse(url).scheme

  har = browser.get_har()
  #with open(os.path.join(os.getcwd(), 'git', '%s.har'%(urlhash)), 'w') as f:
  #  f.write(har)
  with gzip.open(os.path.join(os.getcwd(), 'git', '%s.har.gz'%(urlhash)), "wb") as f:
    f.write(har.encode())
  commit_files.append(os.path.join(os.getcwd(), 'git', '%s.har.gz'%(urlhash)))
  if urlhash not in urlhashes:
    urlhashes[urlhash] = url

  resources = []
  for entry in json.loads(browser.get_har())['log']['entries']:
    if entry['request']['url'] == url:
      #print(entry['response']['content']['text'])
      index=entry['response']['content']['text'].find(".pdf", 0)
      while index > 0:
        if index - 512 < 0:
          start = 0
        else:
          start = index - 512
        try:
          resource = re.findall( pdfregex, entry['response']['content']['text'][start:index+4])[-1] #only last occurance

          if "file://" in resource:
            index=entry['response']['content']['text'].find(".pdf", index+4)
            continue
          if "http" not in resource:
            resource = "%s://%s/%s"%( urlscheme, urlbase, resource.lstrip('/') )
          print("Resource found: %s"%(resource) )
          resources.append(resource)
          if config.config_object['SPN2']['enabled']:
            spn2.submit(resource)
        except Exception as e:
          print(e)
          pass
        index=entry['response']['content']['text'].find(".pdf", index+4)
      break #found exact url and no need to search other urls
  
  if len(resources):
    resourcedir = os.path.join( config.config_object['GIT']['dir'], urlhash )
    os.makedirs( resourcedir, exist_ok=True )
    commit_files.append( resourcedir )
    for resource in resources:
      filename = resource.rsplit('/', 1)[1]
      resp     = requests.get(resource)
      with open(os.path.join(resourcedir, filename), 'wb') as f:
        f.write(resp.content)
    print()

  del browser
  del m

with open(os.path.join(os.getcwd(), 'git', 'index.csv'), 'w') as f:
  f.write("hash;url\n")
  for hash in dict( sorted(urlhashes.items(), key=lambda x:x[1]) ):
    f.write( "%s;%s\n"%(hash, urlhashes[hash].strip() ) )

#print(commit_files)
if config.config_object['GIT']['commit']:
  repo.index.add(commit_files)
  repo.index.commit("Update %s"%(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
  repo.remote('origin').push()
#shutil.rmtree( os.path.join(os.getcwd(), 'git') )

