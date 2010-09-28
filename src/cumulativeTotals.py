#!/usr/bin/env python
# encoding: utf-8

import os
from tempfile import NamedTemporaryFile
from statistics import Statistics
from util import *

plot = """
received = Drop[Sort[Import["$RECEIVED_TEMPORARY_FILE_NAME"]], -1];
sent = Drop[Sort[Import["$SENT_TEMPORARY_FILE_NAME"]], -1];
Export["output/cumulativeTotals.pdf", DateListPlot[{received, sent}, Joined -> True, PlotStyle -> Thick]];
Exit[];
"""

stats = Statistics()
stats.load()

receivedTotals = {}
sentTotals = {}
cumulativeReceived = cumulativeSent = 0
receivedCSV = ""
sentCSV = ""

for (date, addresses) in sorted(stats.receivedDateAddressCounts.items()):
    cumulativeReceived += sum([count for (addr, count) in addresses.items()])
    receivedCSV += "{0},{1}\n".format(date, cumulativeReceived)

for (date, addresses) in sorted(stats.sentDateAddressCounts.items()):
    cumulativeSent += sum([count for (addr, count) in addresses.items()])
    sentCSV += "{0},{1}\n".format(date, cumulativeSent)

receivedTemp = NamedTemporaryFile(suffix=".csv", delete=False)
receivedTemp.write(receivedCSV)
receivedTemp.close()

sentTemp = NamedTemporaryFile(suffix=".csv", delete=False)
sentTemp.write(sentCSV)
sentTemp.close()

mathematica(plot.replace("$RECEIVED_TEMPORARY_FILE_NAME", receivedTemp.name).replace("$SENT_TEMPORARY_FILE_NAME", sentTemp.name))

os.remove(sentTemp.name)
os.remove(receivedTemp.name)