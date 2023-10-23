#!/usr/bin/python3

from Crypto.PublicKey import RSA

class Cryptokeys:
  def __init__(self):
    self.key = None
    pass

  def generate(self, keybits=2048):
    self.key = RSA.generate(keybits)

  def load_from_string(self, string):
    self.key = RSA.importKey(string)

  def private_key(self):
    return self.key.export_key().decode()

  def public_key(self):
    return self.key.publickey().export_key().decode()

  def openssh_public_key(self):
    return self.key.public_key().export_key('OpenSSH').decode()

if __name__ == "__main__":

  keystring = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
J/LNtwSZfOgIgxAAAAEmpoZXJtYW5zQGthbnRvb3JwYw==
-----END OPENSSH PRIVATE KEY-----"""
  key = Cryptokeys()
  key.load_from_string(keystring)
  sys.exit(0)

  key.generate(keybits=2048)
  print( key.private_key() )
  print()
  print( key.public_key() )
  print()
  print( key.openssh_public_key() )
