#!/usr/bin/env python
# encoding: utf-8

import json
import re
import os
import emlx
import datetime
import codecs
from email.utils import parsedate
from collections import defaultdict
from progressbar import ProgressBar, Percentage, Bar, RotatingMarker, ETA

def writeFile(filename, contents):
    out = codecs.open(filename, encoding='utf-8', mode='w+')
    out.write(contents)
    out.close()

gmailRoot = os.path.expanduser("~/Library/Mail/IMAP-hortont424@imap.gmail.com/[Gmail]/All Mail.imapmbox/Messages")
myAddresses = set([s.lower() for s in ["hortont424@gmail.com", "hortot2@rpi.edu", "tim@hortont.com", "hortont@svn.gnome.org", "thorton@qualcomm.com", "hortont@git.gnome.org", "hortont@gnome.org", "rhorton16@adelphia.net", "rhorton16@comcast.net", "tphorton@uvm.edu", "internote-andros@lists.sourceforge.net"]])
badEmailRegex='[a-zA-Z0-9+_\-\.]+@[0-9a-zA-Z][.-0-9a-zA-Z]*.[a-zA-Z]+'

lostEmailsAddresses = lostEmailsDate = 0
sentAddressCounts = defaultdict(int)
recievedAddressCounts = defaultdict(int)
sentDateAddressCounts = defaultdict(lambda : defaultdict(int))
recievedDateAddressCounts = defaultdict(lambda : defaultdict(int))
foreignAddresses = set()

emailFiles = []

for root, dirs, files in os.walk(gmailRoot):
    for name in files:
        filename = os.path.join(root, name)

        if filename.endswith(".emlx"):
            emailFiles.append(filename)

progress = ProgressBar(widgets=["Parsing Mail: ", Percentage(), " ", Bar(), " ", ETA()],
                       maxval=len(emailFiles)).start()

for filename in emailFiles:
    progress.update(progress.currval + 1)

    email = emlx.emlx(filename)

    toString = email.message["to"]
    fromString = email.message["from"]

    if (not toString) or (not fromString):
        lostEmailsAddresses += 1
        continue

    toAddresses = set(re.findall(badEmailRegex, toString.lower().replace("\n", " ")))
    fromAddresses = set(re.findall(badEmailRegex, fromString.lower().replace("\n", " ")))

    if fromAddresses.intersection(myAddresses):
        sentMessage = True
        # This is a sent message
        for addr in toAddresses:
            sentAddressCounts[addr] += 1
    else:
        sentMessage = False
        # This is a recieved message
        for addr in fromAddresses:
            recievedAddressCounts[addr] += 1

    foreignAddresses.update(fromAddresses.union(toAddresses).difference(myAddresses))

    messageDate = parsedate(email.message["date"])

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
            recievedDateAddressCounts[messageDate][addr] += 1

progress.finish()

writeFile("foreignAddresses.json", json.dumps(list(foreignAddresses)))
writeFile("sentAddressCounts.json", json.dumps(dict(sentAddressCounts)))
writeFile("recievedAddressCounts.json", json.dumps(dict(recievedAddressCounts)))
writeFile("sentDateAddressCounts.json", json.dumps(sentDateAddressCounts))
writeFile("recievedDateAddressCounts.json", json.dumps(recievedDateAddressCounts))
writeFile("metadata.json", json.dumps({"lostEmailsAddresses": lostEmailsAddresses, "lostEmailsDate": lostEmailsDate}))