.PHONY: clean

DBFILES = db/foreignAddresses.json \
          db/metadata.json \
          db/receivedAddressCounts.json \
          db/receivedDateAddressCounts.json \
          db/sentAddressCounts.json \
          db/sentDateAddressCounts.json

STATSFILES = output/totalPerMonth.pdf \
             output/cumulativeTotals.pdf \
             output/relationshipSidedness.pdf

CONFIGFILE = config/config.json

all: $(DBFILES) $(STATSFILES)

output/%.pdf:: src/%.py $(DBFILES)
	mkdir -p output
	python $<

$(DBFILES): $(CONFIGFILE) src/main.py src/util.py
	mkdir -p db
	python ./src/main.py

clean:
	rm -f $(DBFILES)
	rm -f $(STATSFILES)
	rm -f ./src/*.pyc
