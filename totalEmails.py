#!/usr/bin/env python
# encoding: utf-8

import json
from operator import itemgetter
from util import *

recievedAddressCounts = json.loads(readFile("recievedAddressCounts.json"))
sentAddressCounts = json.loads(readFile("sentAddressCounts.json"))

for (addr, count) in sorted(sentAddressCounts.items(), key=itemgetter(1)):
    print "{0}\t\t{1}".format(addr.ljust(15), repr(count).rjust(4))