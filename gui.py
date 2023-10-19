#!/usr/bin/python3

import PySimpleGUI as sg
import os
from har import Har
import webbrowser
import config
from git import Repo
from git import Git
import time

version = 'v1.0'

har = Har()

urls = {}

form_rows = [
             [sg.Listbox(values=[], key="URLS", size=(70, 6))],
             [[sg.Button('Export', enable_events=True)], [sg.Button('Versions', enable_events=True)]],
             [sg.Button('Exit')],
]

sg.theme('DefaultNoMoreNagging')
window = sg.Window('Ella forensic website tool %s by Jeroen Hermans'%(version), form_rows, finalize=True)

if not os.path.isdir( config.gitdir ):
  os.makedirs( config.gitdir, exist_ok=True )
  print("Cloning %s into %s"%(config.git['url'], config.gitdir))
  repo = Repo.clone_from(config.git['url'], config.gitdir, env=dict(GIT_SSH_COMMAND=config.git['ssh_cmd']))

with open(os.path.join( config.gitdir, 'index.csv' ), 'r') as f:
  lines = f.readlines()

  for line in lines:
    if line != '' and not line.startswith('#') and not line.startswith('hash'):
      h,u = line.split(';')
      urls[u.strip()] = h
window["URLS"].update( list( urls.keys() ) )

while True:
  event, values = window.read()
  if event in (sg.WIN_CLOSED, 'Exit'):
    break
  elif event == 'Export':
    har.load_har(os.path.join(config.gitdir, "%s.har.gz"%(urls[values['URLS'][0]]) ) )
    webbrowser.open(os.path.join('temp', "%s.html"%(har.basehash) ) )
  elif event == 'Versions':
    repo = Repo(config.gitdir)
    commits = list( repo.iter_commits(all=True, max_count=10, paths="%s.har"%(urls[values['URLS'][0]])) )
    print("%s.har"%(urls[values['URLS'][0]]))
    for commit in commits:
      tree = commit.tree
      files_and_dirs = [(entry, entry.name, entry.type) for entry in tree]
      for fad in files_and_dirs:
        if fad[2] == 'blob' and fad[1] == "%s.har"%(urls[values['URLS'][0]]):
          commit_time = time.gmtime(commit.authored_date-commit.committer_tz_offset)
          print( "%s %02d-%02d-%04d %02d:%02d:%02d %s"%( commit.hexsha, commit_time.tm_mday, commit_time.tm_mon, commit_time.tm_year, commit_time.tm_hour, commit_time.tm_min, commit_time.tm_sec, commit.message ) )
          break
      #.strftime("%d-%m-%Y %H:%M:%S")
      #print("%s %32s %s"%(commit.binsha, tree.name, commit.message) )

window.close()

