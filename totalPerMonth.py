#!/usr/bin/env python
# encoding: utf-8

import json
from tempfile import NamedTemporaryFile
from collections import defaultdict
from util import *

plot = """
data = Drop[Sort[Import["$TEMPORARY_FILE_NAME"]], -1];
received = {DateList[#[[1]]], #[[2]]} & /@ data;
sent = {DateList[#[[1]]], #[[3]]} & /@ data;
Export["totalPerMonth.pdf", DateListPlot[{received, sent}, Joined -> True, PlotStyle -> Thick]];
Exit[];
"""

receivedDateAddressCounts = json.loads(readFile("receivedDateAddressCounts.json"))
sentDateAddressCounts = json.loads(readFile("sentDateAddressCounts.json"))

dateTotals = defaultdict(lambda : defaultdict(int))
csvdata = ""

for (date, addresses) in receivedDateAddressCounts.items():
    date = ".".join(date.split(".")[:2] + ["1"])
    dateTotals[date]["received"] += sum([count for (addr, count) in addresses.items()])

for (date, addresses) in sentDateAddressCounts.items():
    date = ".".join(date.split(".")[:2] + ["1"])
    dateTotals[date]["sent"] += sum([count for (addr, count) in addresses.items()])

for (date, counts) in dateTotals.items():
    received = sent = 0

    if "received" in counts:
        received = counts["received"]

    if "sent" in counts:
        sent = counts["sent"]

    csvdata += "{0},{1},{2}\n".format(date, received, sent)

temp = NamedTemporaryFile(suffix=".csv", delete=False)
temp.write(csvdata)
temp.close()

mathematica(plot.replace("$TEMPORARY_FILE_NAME", temp.name))