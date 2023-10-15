#!/usr/bin/python3

from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from git import Repo
from git import Git
import os, sys, shutil
import hashlib
from datetime import datetime
from urllib.parse import urlparse
import json
import re
import requests
import config

if os.path.isdir( config.gitdir ):
  print("repo exists in %s, pulling..."%(config.gitdir))
  repo = Repo( config.gitdir )
  repo.git.update_environment(GIT_SSH_COMMAND=config.git['ssh_cmd'])
  repo.remotes.origin.pull()
else:
  os.makedirs( config.gitdir, exist_ok=True )
  print("Cloning %s into %s"%(config.git['url'], config.gitdir))
  repo = Repo.clone_from(config.git['url'], os.path.join(os.getcwd(), 'git'),env=dict(GIT_SSH_COMMAND=config.git['ssh_cmd']))

class Browser:
  def __init__(self):
    self.seleniumwire_options = {
        'enable_har': True  # Capture HAR data, retrieve with driver.har
    }
    self.options = Options()
    self.options.headless = True
    self.options.add_argument("--headless")
    try:
      self.driver = webdriver.Firefox(seleniumwire_options=self.seleniumwire_options, options=self.options)
    except Exception as e:
        print(e)
        sys.exit(0)

  def __del__(self):
    self.driver.quit()

  def get(self, url):
    self.driver.get(url)

  def get_har(self):
    return self.driver.har

urls = []
with open('urls.csv', 'r') as f:
  lines = f.readlines()
  
  for line in lines:
    if line != '' and not line.startswith('#'):
      urls.append(line)

commit_files = [os.path.join(os.getcwd(), 'git', 'index.csv')]
urlhashes = {}
with open(os.path.join(os.getcwd(), 'git', 'index.csv'), 'r') as f:
  lines = f.readlines()
  for line in lines:
    if line.startswith('hash;'):
      continue
    try:
      h,u = line.split(';')
      urlhashes[h] = u
    except:
      pass

for url in urls:
  m = hashlib.sha1()
  browser = Browser()
  print("Getting url %s"%(url))
  browser.get(url)
  m.update(url.encode())
  urlhash   = m.hexdigest()
  urlbase   = urlparse(url).netloc
  urlscheme = urlparse(url).scheme

  with open(os.path.join(os.getcwd(), 'git', '%s.har'%(urlhash)), 'w') as f:
    f.write(browser.get_har())
  commit_files.append(os.path.join(os.getcwd(), 'git', '%s.har'%(urlhash)))
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
          resource = re.findall(config.pdfregex, entry['response']['content']['text'][start:index+4])[-1] #only last occurance

          if "file://" in resource:
            index=entry['response']['content']['text'].find(".pdf", index+4)
            continue
          if "http" not in resource:
            resource = "%s://%s/%s"%( urlscheme, urlbase, resource.lstrip('/') )
          print("Resource found: %s"%(resource) )
          resources.append(resource)
        except Exception as e:
          print(e)
          pass
        index=entry['response']['content']['text'].find(".pdf", index+4)
      break #found exact url and no need to search other urls
  
  if len(resources):
    resourcedir = os.path.join( config.gitdir, urlhash )
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

repo.index.add(commit_files)
repo.index.commit("Update %s"%(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
repo.remote('origin').push()
#shutil.rmtree( os.path.join(os.getcwd(), 'git') )
