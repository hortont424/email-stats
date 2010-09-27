#!/usr/bin/env python
# encoding: utf-8
"""
emlx.py

Created by Rui Carmo on 2008-03-03.
Released under the MIT license
"""

import email

class emlx:
  def __init__(self, filename):
    self.filename = filename
    self.load()

  def load(self):
    self.fh = open(self.filename,'rb')
    self.bytes = int(self.fh.readline().strip())
    self.message = email.message_from_string(self.fh.read(self.bytes))
    self.plist = ''.join(self.fh.readlines())
    self.fh.close()

  def save(self, filename):
    fh = open(filename,'wb')
    # get the payload length
    bytes = len(str(self.message))
    fh.write("%d\n%s%s" % (bytes, self.message, self.plist))
    fh.close()
