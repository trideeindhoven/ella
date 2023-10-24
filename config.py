#!/usr/bin/python3

from configparser import ConfigParser
import sys

class Config:
  def __init__(self):
    self.config_object = ConfigParser()
    try:
      self.config_object.read("config.ini")
    except Exception as e:
      print("Unable to read config file config.ini")
      print(e)

  def write(self):
    with open('config.ini', 'w') as configfile:
      self.config_object.write(configfile)

if __name__ == '__main__':
  from pprint import pprint
  config = Config()
  pprint( config )
  pprint( config.config_object )

  #for key in  config.config_object['GIT']:
  #  print("%s = %s"%(key, config.config_object['GIT'][key]))
  #print( config.config_object['GIT']['url'] )

  #config.config_object['GIT']['url'] = "https://www.nu.nl"

  #for key in config.config_object['GIT']:
  #  print("%s = %s"%(key, config.config_object['GIT'][key]))

