#!/usr/bin/python3

from configparser import ConfigParser
import sys

config_object = ConfigParser()

try:
  config_object.read("config.ini")
except:
  print("Unable to read config file config.ini")
  sys.exit(0)

from pprint import pprint
for key in  config_object['GIT']:
  print("%s = %s"%(key, config_object['GIT'][key]))
print( config_object['GIT']['url'] )

config_object['GIT']['url'] = "https://www.nu.nl"

for key in  config_object['GIT']:
  print("%s = %s"%(key, config_object['GIT'][key]))

