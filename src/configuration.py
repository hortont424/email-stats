#!/usr/bin/env python
# encoding: utf-8

import json
import re
import os
from util import *

class Configuration(object):
    def __init__(self):
        super(Configuration, self).__init__()
        self.gmailRoot = ""
        self.myAddresses = set()
        self.metacontactMapping = {}
        self.metacontactExpressions = {}

    def load(self, filename):
        configJSON = json.loads(readFile(filename))

        self.gmailRoot = os.path.expanduser(configJSON["gmailRoot"])
        self.myAddresses = set([s.lower() for s in configJSON["myAddresses"]])

        self.metacontactMapping = {}
        self.metacontactExpressions = {}
        for metacontact in configJSON["metacontacts"]:
            if "addresses" in metacontact:
                for addr in metacontact["addresses"]:
                    self.metacontactMapping[addr] = metacontact["name"]
            if "expressions" in metacontact:
                for expr in metacontact["expressions"]:
                    self.metacontactExpressions[expr] = metacontact["name"]

        for addr in self.myAddresses:
            self.metacontactMapping[addr] = "Me"

        self.myAddresses.add("Me")

    def mapAddress(self, addr):
        if addr in self.metacontactMapping:
            addr = self.metacontactMapping[addr]
        for expr in self.metacontactExpressions:
            if re.match(expr, addr):
                addr = self.metacontactExpressions[expr]

        return addr