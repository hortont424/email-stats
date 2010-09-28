.PHONY: all clean db

all: db stats

db:
	mkdir -p db
	python ./src/main.py

stats:
	mkdir -p output
	python ./src/totalPerMonth.py
	python ./src/totalEmails.py

clean:
	rm -rf ./output
	rm -rf ./db
	rm -f ./src/*.pyc