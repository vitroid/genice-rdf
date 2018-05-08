.DELETE_ON_ERROR:
OS=$(shell uname)
ifeq ($(OS), Darwin)
	DEST=~/Library/Application\ Support/GenIce
else
	DEST=~/.genice
endif

test: 5.rdf
%.rdf: genice_rdf/formats/_RDF.py Makefile
	genice $* -r 3 3 3 -f _RDF > $@
check:
	./setup.py check
install:
	./setup.py install
pypi: check
	./setup.py sdist bdist_wheel upload
clean:
	-rm $(ALL) *~ */*~ *.rdf
	-rm -rf build dist *.egg-info
	-find . -name __pycache__ | xargs rm -rf
