#!/usr/bin/env python
# encoding: utf-8

import os
from tempfile import NamedTemporaryFile
from operator import itemgetter
from statistics import Statistics
from util import *

plot = """
data = Import["$TEMPORARY_FILE_NAME"];
colors = If[#[[2]] > 1, LightBlue, LightGreen] & /@ data;
Export["output/relationshipSidedness.pdf",
    BarChart[Last /@ data, ChartLabels -> First /@ data,
             BarOrigin -> Left, ChartStyle -> colors],
    ImageSize->600]
Exit[];
"""

stats = Statistics()
stats.load()

csv = ""
netAddressCounts = []
totals = {}

for addr in stats.foreignAddresses:
    receivedCount = sentCount = 0

    if addr in stats.sentAddressCounts:
        sentCount = stats.sentAddressCounts[addr]

    if addr in stats.receivedAddressCounts:
        receivedCount = stats.receivedAddressCounts[addr]

    if receivedCount > 0 and sentCount > 0:
        totals[addr] = sentCount + receivedCount

for (addr, count) in sorted(totals.items(), key=itemgetter(1), reverse=True)[:25]:
    receivedCount = sentCount = 0

    if addr in stats.sentAddressCounts:
        sentCount = stats.sentAddressCounts[addr]

    if addr in stats.receivedAddressCounts:
        receivedCount = stats.receivedAddressCounts[addr]
        netAddressCounts.append([addr, float(sentCount) / float(receivedCount)])

for (addr, count) in sorted(netAddressCounts, key=itemgetter(1)):
    csv += "{0},{1}\n".format(addr, count)

temp = NamedTemporaryFile(suffix=".csv", delete=False)
temp.write(csv)
temp.close()

mathematica(plot.replace("$TEMPORARY_FILE_NAME", temp.name))

os.remove(temp.name)