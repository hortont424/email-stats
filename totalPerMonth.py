#!/usr/bin/env python
# encoding: utf-8

import json
from tempfile import NamedTemporaryFile
from collections import defaultdict
from util import *

plot = """
data = Drop[Sort[Import["$TEMPORARY_FILE_NAME"]], -1];
recieved = {DateList[#[[1]]], #[[2]]} & /@ data;
sent = {DateList[#[[1]]], #[[3]]} & /@ data;
Export["totalPerMonth.pdf", DateListPlot[{recieved, sent}, Joined -> True, PlotStyle -> Thick]];
Exit[];
"""

recievedDateAddressCounts = json.loads(readFile("recievedDateAddressCounts.json"))
sentDateAddressCounts = json.loads(readFile("sentDateAddressCounts.json"))

dateTotals = defaultdict(lambda : defaultdict(int))
csvdata = ""

for (date, addresses) in recievedDateAddressCounts.items():
    date = ".".join(date.split(".")[:2] + ["1"])
    dateTotals[date]["recieved"] += sum([count for (addr, count) in addresses.items()])

for (date, addresses) in sentDateAddressCounts.items():
    date = ".".join(date.split(".")[:2] + ["1"])
    dateTotals[date]["sent"] += sum([count for (addr, count) in addresses.items()])

for (date, counts) in dateTotals.items():
    recieved = sent = 0

    if "recieved" in counts:
        recieved = counts["recieved"]

    if "sent" in counts:
        sent = counts["sent"]

    csvdata += "{0},{1},{2}\n".format(date, recieved, sent)

temp = NamedTemporaryFile(suffix=".csv", delete=False)
temp.write(csvdata)
temp.close()

mathematica(plot.replace("$TEMPORARY_FILE_NAME", temp.name))