#!/usr/bin/env python
# encoding: utf-8

import json
import re
import os
import email
import email.parser
import datetime
from email.utils import parsedate
from collections import defaultdict
from progressbar import ProgressBar, Percentage, Bar, RotatingMarker, ETA
from util import *

config = json.loads(readFile("config.json"))
gmailRoot = os.path.expanduser(config["gmailRoot"])
myAddresses = set([s.lower() for s in config["myAddresses"]])

badEmailRegex = '[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}'

metacontactMapping = {}
metacontactExpressions = {}
for metacontact in config["metacontacts"]:
    if "addresses" in metacontact:
        for addr in metacontact["addresses"]:
            metacontactMapping[addr] = metacontact["name"]
    if "expressions" in metacontact:
        for expr in metacontact["expressions"]:
            metacontactExpressions[expr] = metacontact["name"]

for addr in config["myAddresses"]:
    metacontactMapping[addr] = "Me"

###

def mapAddress(addr):
    if addr in metacontactMapping:
        addr = metacontactMapping[addr]
    for expr in metacontactExpressions:
        if re.match(expr, addr):
            addr = metacontactExpressions[expr]

    return addr

###

lostEmailsAddresses = lostEmailsDate = 0
sentAddressCounts = defaultdict(int)
receivedAddressCounts = defaultdict(int)
sentDateAddressCounts = defaultdict(lambda : defaultdict(int))
receivedDateAddressCounts = defaultdict(lambda : defaultdict(int))
foreignAddresses = set()

emailFiles = []

for root, dirs, files in os.walk(gmailRoot):
    for name in files:
        filename = os.path.join(root, name)

        if filename.endswith(".emlx"):
            emailFiles.append(filename)

progress = ProgressBar(widgets=["Parsing Mail: ", Percentage(), " ", Bar(), " ", ETA()],
                       maxval=len(emailFiles)).start()

parser = email.parser.Parser()

for filename in emailFiles:
    progress.update(progress.currval + 1)

    fh = open(filename, 'rb')
    message = parser.parsestr(fh.read(int(fh.readline().strip())), headersonly=True)
    fh.close()

    toString = message["to"]
    fromString = message["from"]

    if (not toString) or (not fromString):
        lostEmailsAddresses += 1
        continue

    toAddresses = set([mapAddress(a) for a in re.findall(badEmailRegex, toString.lower().replace("\n", " "))])
    fromAddresses = set([mapAddress(a) for a in re.findall(badEmailRegex, fromString.lower().replace("\n", " "))])

    myAddresses.add("Me")

    if fromAddresses.intersection(myAddresses):
        sentMessage = True
        # This is a sent message
        for addr in toAddresses:
            sentAddressCounts[addr] += 1
    else:
        sentMessage = False
        # This is a received message
        for addr in fromAddresses:
            receivedAddressCounts[addr] += 1

    foreignAddresses.update(fromAddresses.union(toAddresses).difference(myAddresses))

    messageDate = parsedate(message["date"])

    if (not messageDate):
        lostEmailsDate += 1
        continue

    messageDate = list(messageDate)
    if messageDate[0] < 1900:
        messageDate[0] += 2000

    try:
        messageDate = datetime.datetime(*messageDate[:7]).date().strftime("%Y.%m.%d")
    except ValueError:
        lostEmailsDate += 1
        continue

    if sentMessage:
        for addr in toAddresses:
            sentDateAddressCounts[messageDate][addr] += 1
    else:
        for addr in fromAddresses:
            receivedDateAddressCounts[messageDate][addr] += 1

progress.finish()

writeFile("foreignAddresses.json", json.dumps(list(foreignAddresses)))
writeFile("sentAddressCounts.json", json.dumps(dict(sentAddressCounts)))
writeFile("receivedAddressCounts.json", json.dumps(dict(receivedAddressCounts)))
writeFile("sentDateAddressCounts.json", json.dumps(sentDateAddressCounts))
writeFile("receivedDateAddressCounts.json", json.dumps(receivedDateAddressCounts))
writeFile("metadata.json", json.dumps({"lostEmailsAddresses": lostEmailsAddresses, "lostEmailsDate": lostEmailsDate}))