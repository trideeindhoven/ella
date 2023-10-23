#!/usr/bin/python3

import requests
import config
import time

class SPN2:
  def __init__(self, access_key, secret_key):
    self.session    = requests.session()
    self.access_key = access_key
    self.secret_key = secret_key
    self.job_id     = None
    
  def submit (self, url):
    headers = {
         "Accept": "application/json",
         "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
         "Authorization": "LOW %s:%s"%( self.access_key, self.secret_key )
    }
    data = {'url': url}

    for _ in range(10):
      resp = self.session.post('https://web.archive.org/save', headers=headers, data=data)
      try:
        self.job_id = resp.json()['job_id']
        break
      except:
        print("ERROR: unable to get job_id from Wayback Machine")
        #print(resp.content)
        time.sleep(30)
    
    return resp.status_code

  def get_status(self):
    url = 'https://web.archive.org/save/status/%s'%(self.job_id)
    resp = self.session.get(url)
    return resp.json()

if __name__ == "__main__":
  spn2 = SPN2(access_key=config.spn2['access_key'], secret_key=config.spn2['secret_key'])
  spn2.submit('https://www.nu.nl')
  print(spn2.get_status())

