PREFIX=/usr/local
BINDIR=$(PREFIX)/bin

all:
	./test_iproute2_parse.py
	./test_system_files_parse.py

clean:
	rm -f *.pyc
	rm -rf tmp

.PHONY: clean
