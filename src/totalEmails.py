#!/usr/bin/env python
# encoding: utf-8

import os
from operator import itemgetter
from statistics import Statistics
from util import *

stats = Statistics()
stats.load()

for (addr, count) in sorted(stats.sentAddressCounts.items(), key=itemgetter(1)):
    print "{0}\t\t{1}".format(addr.ljust(15), repr(count).rjust(4))