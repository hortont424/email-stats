#!/usr/bin/env python
# encoding: utf-8

import json
import os
import email
import re
import email.parser
import datetime
import email.utils
from progressbar import ProgressBar, Percentage, Bar, RotatingMarker, ETA
from configuration import Configuration
from statistics import Statistics

def extractEmailAddresses(addressString):
    emailRegex = '[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}'
    return re.findall(emailRegex, addressString.lower().replace("\n", " "))

def mapEmailAddresses(config, addresses):
    return set([config.mapAddress(a) for a in addresses])

def listEmailFiles(root):
    emailFiles = []

    for root, dirs, files in os.walk(root):
        for name in files:
            filename = os.path.join(root, name)

            if filename.endswith(".emlx"):
                emailFiles.append(filename)

    return emailFiles

def readEmailHeaders(filename):
    if not hasattr(readEmailHeaders, "parser"):
        readEmailHeaders.parser = email.parser.Parser()

    fh = open(filename, 'rb')
    message = readEmailHeaders.parser.parsestr(fh.read(int(fh.readline().strip())), headersonly=True)
    fh.close()

    return message

def validateEmailDate(messageDate):
    if (not messageDate):
        return None

    messageDate = list(messageDate)

    if messageDate[0] < 1900:
        messageDate[0] += 2000

    if messageDate[0] > datetime.date.today().year:
        return None

    try:
        messageDate = datetime.date(*messageDate[:3]).strftime("%Y.%m.%d")
    except ValueError:
        return None

    return messageDate

def updateStatistics(stats, config, filename):
    message = readEmailHeaders(filename)

    toString = message["to"]
    fromString = message["from"]

    if (not toString) or (not fromString):
        stats.lostEmailsAddresses += 1
        return

    toAddresses = mapEmailAddresses(config, extractEmailAddresses(toString))
    fromAddresses = mapEmailAddresses(config, extractEmailAddresses(fromString))

    if fromAddresses.intersection(config.myAddresses):
        sentMessage = True
        # This is a sent message
        for addr in toAddresses:
            stats.sentAddressCounts[addr] += 1
    else:
        sentMessage = False
        # This is a received message
        for addr in fromAddresses:
            stats.receivedAddressCounts[addr] += 1

    stats.foreignAddresses.update(fromAddresses.union(toAddresses).difference(config.myAddresses))

    messageDate = validateEmailDate(email.utils.parsedate(message["date"]))

    if not messageDate:
        stats.lostEmailsDate += 1
        return

    if sentMessage:
        for addr in toAddresses:
            stats.sentDateAddressCounts[messageDate][addr] += 1
    else:
        for addr in fromAddresses:
            stats.receivedDateAddressCounts[messageDate][addr] += 1

def main():
    config = Configuration()
    config.load("config/config.json")

    emailFiles = listEmailFiles(config.gmailRoot)
    stats = Statistics()

    progress = ProgressBar(widgets=["Parsing Mail: ", Percentage(), " ", Bar(), " ", ETA()],
                           maxval=len(emailFiles)).start()

    for filename in emailFiles:
        progress.update(progress.currval + 1)
        updateStatistics(stats, config, filename)

    progress.finish()

    stats.save()

if __name__ == "__main__":
    main()