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
    """
    Given a string, extract all valid email addresses.

    This function is far from perfect, as it's very hard to match email addresses with a
    regular expression. However, it seems to work on the entirety of my mail database.
    """
    emailRegex = '[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}'
    return re.findall(emailRegex, addressString.lower().replace("\n", " "))

def mapEmailAddresses(config, addresses):
    """
    Given an email address, map it to the matching metacontact if one exists.
    """
    return set([config.mapAddress(a) for a in addresses])

def listEmailFiles(root):
    """
    Given a directory, recursively generate a list of all emlx files.
    """
    emailFiles = []

    for root, dirs, files in os.walk(root):
        for name in files:
            filename = os.path.join(root, name)

            if filename.endswith(".emlx"):
                emailFiles.append(filename)

    return emailFiles

def readEmailHeaders(filename):
    """
    Given the name of a file, load it, parse its headers, and return an email.message object.
    This specifically parses Apple Mail emlx files, but could be modified to deal with
    bare RFC 2822 messages.
    """
    if not hasattr(readEmailHeaders, "parser"):
        readEmailHeaders.parser = email.parser.Parser()

    fh = open(filename, 'rb')
    message = readEmailHeaders.parser.parsestr(fh.read(int(fh.readline().strip())), headersonly=True)
    fh.close()

    return message

def validateEmailDate(messageDate):
    """
    Parse, attempt to correct, and validate the given RFC 2822-compliant date.
    This makes some assumptions: years less than 1900 should be bumped up by 2000,
    to solve the case where we only have two digits (this works for my mail, since it's all
    post-2003); years greater than the current year are invalid and rejected.
    """
    messageDate = email.utils.parsedate(messageDate)

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
    """
    Given the name of an email file, parse it, updating the statistics with the collected information.
    """
    message = readEmailHeaders(filename)

    toString = "{0} {1}".format(message["to"], message["cc"])
    fromString = message["from"]

    # We require To and From headers
    if (not toString) or (not fromString):
        stats.lostEmailsAddresses += 1
        return

    # Extract email addresses and substitute in metacontacts
    toAddresses = mapEmailAddresses(config, extractEmailAddresses(toString))
    fromAddresses = mapEmailAddresses(config, extractEmailAddresses(fromString))

    # If any of the From addresses appear to be one of ours, we can assume that
    # we are the originator of the message
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

    # Add any addresses in all fields which are not ours to the list of foreign addresses
    stats.foreignAddresses.update(fromAddresses.union(toAddresses).difference(config.myAddresses))

    messageDate = validateEmailDate(message["date"])

    if not messageDate:
        stats.lostEmailsDate += 1
        return

    # Update the per-day per-address email count statistics
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