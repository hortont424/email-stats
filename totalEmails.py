#!/usr/bin/env python
# encoding: utf-8

import json
from operator import itemgetter
from util import *

receivedAddressCounts = json.loads(readFile("receivedAddressCounts.json"))
sentAddressCounts = json.loads(readFile("sentAddressCounts.json"))

for (addr, count) in sorted(sentAddressCounts.items(), key=itemgetter(1)):
    print "{0}\t\t{1}".format(addr.ljust(15), repr(count).rjust(4))