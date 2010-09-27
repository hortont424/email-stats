.PHONY: all clean

all:
	python ./createEmailDB.py
	python ./totalPerMonth.py
	python ./totalEmails.py

clean:
	rm -f *.pdf
	rm -f foreignAddresses.json
	rm -f metadata.json
	rm -f receivedAddressCounts.json
	rm -f receivedDateAddressCounts.json
	rm -f sentAddressCounts.json
	rm -f sentDateAddressCounts.json
	rm -f *.pyc