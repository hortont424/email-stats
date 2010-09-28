import json
from collections import defaultdict
from util import *

class Statistics(object):
    def __init__(self):
        super(Statistics, self).__init__()

        self.lostEmailsAddresses = 0
        self.lostEmailsDate = 0

        self.sentAddressCounts = defaultdict(int)
        self.receivedAddressCounts = defaultdict(int)
        self.sentDateAddressCounts = defaultdict(lambda : defaultdict(int))
        self.receivedDateAddressCounts = defaultdict(lambda : defaultdict(int))
        self.foreignAddresses = set()

    def save(self):
        writeFile("db/foreignAddresses.json", json.dumps(list(self.foreignAddresses)))
        writeFile("db/sentAddressCounts.json", json.dumps(dict(self.sentAddressCounts)))
        writeFile("db/receivedAddressCounts.json", json.dumps(dict(self.receivedAddressCounts)))
        writeFile("db/sentDateAddressCounts.json", json.dumps(self.sentDateAddressCounts))
        writeFile("db/receivedDateAddressCounts.json", json.dumps(self.receivedDateAddressCounts))
        writeFile("db/metadata.json", json.dumps({"lostEmailsAddresses": self.lostEmailsAddresses,
                                                  "lostEmailsDate": self.lostEmailsDate}))

    def load(self):
        self.foreignAddresses = json.loads(readFile("db/foreignAddresses.json"))
        self.sentAddressCounts = json.loads(readFile("db/sentAddressCounts.json"))
        self.receivedAddressCounts = json.loads(readFile("db/receivedAddressCounts.json"))
        self.sentDateAddressCounts = json.loads(readFile("db/sentDateAddressCounts.json"))
        self.receivedDateAddressCounts = json.loads(readFile("db/receivedDateAddressCounts.json"))
        self.metadata = json.loads(readFile("db/metadata.json"))

        self.lostEmailsAddresses = self.metadata["lostEmailsAddresses"]
        self.lostEmailsDate = self.metadata["lostEmailsDate"]