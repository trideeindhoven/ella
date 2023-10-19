#!/usr/bin/python3

from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options

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

