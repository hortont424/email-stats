.PHONY: clean

DBFILES = db/foreignAddresses.json \
          db/metadata.json \
          db/receivedAddressCounts.json \
          db/receivedDateAddressCounts.json \
          db/sentAddressCounts.json \
          db/sentDateAddressCounts.json

STATSFILES = output/totalPerMonth.pdf

CONFIGFILE = config/config.json

output/%.pdf:: src/%.py $(DBFILES)
	mkdir -p ./output
	python $<

$(DBFILES): $(CONFIGFILE) src/main.py src/util.py
	mkdir -p db
	python ./src/main.py

all: $(DBFILES) $(STATSFILES)

clean:
	rm -rf ./output
	rm -rf ./db
	rm -f ./src/*.pyc