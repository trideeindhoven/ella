#!/usr/bin/python3

from Crypto.PublicKey import RSA

class Cryptokeys:
  def __init__(self, keybits=2048):
    self.key = RSA.generate(keybits)

  def private_key(self):
    return self.key.export_key().decode()

  def public_key(self):
    return self.key.publickey().export_key().decode()

  def openssh_public_key(self):
    return self.key.public_key().export_key('OpenSSH').decode()

if __name__ == "__main__":
  key = Cryptokeys()
  print( key.private_key() )
  print()
  print( key.public_key() )
  print()
  print( key.openssh_public_key() )
