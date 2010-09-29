#!/usr/bin/env python
# encoding: utf-8

import os
from tempfile import NamedTemporaryFile
from operator import itemgetter
from collections import defaultdict
from statistics import Statistics
from util import *

plot = """
data = Drop[Sort[Import["$TEMPORARY_FILE_NAME"]], -1];

tp = Transpose[data];
dates = First[tp];
tp = Rest[tp];
dataLists = Map[Thread[{dates, #}] &, tp]

Export["output/personalTotalPerMonth.pdf", DateListPlot[dataLists, Joined -> True, PlotStyle -> Thick, PlotRange -> All], ImageSize->600];
Exit[];
"""

stats = Statistics()
stats.load()

topAddresses = []
dateTotals = defaultdict(lambda : defaultdict(int))
csvdata = ""

for (addr, count) in sorted(stats.sentAddressCounts.items(), key=itemgetter(1), reverse=True)[:10]:
    topAddresses.append(addr)

for (date, addresses) in stats.receivedDateAddressCounts.items():
    date = ".".join(date.split(".")[:2] + ["01"])
    for addr in topAddresses:
        if addr in addresses:
            dateTotals[date][addr] += addresses[addr]

#for (date, addresses) in stats.sentDateAddressCounts.items():
#    date = ".".join(date.split(".")[:2] + ["01"])
#    for addr in topAddresses:
#        if addr in addresses:
#            dateTotals[date][addr] += addresses[addr]

for (date, addressCounts) in sorted(dateTotals.items()):
    dateline = "{0},".format(date)

    for address in topAddresses:
        if address in addressCounts:
            dateline += repr(addressCounts[address]) + ","
        else:
            dateline += "0,"

    dateline = dateline[:-1]
    csvdata += dateline + "\n"

temp = NamedTemporaryFile(suffix=".csv", delete=False)
temp.write(csvdata)
temp.close()

mathematica(plot.replace("$TEMPORARY_FILE_NAME", temp.name))

os.remove(temp.name)