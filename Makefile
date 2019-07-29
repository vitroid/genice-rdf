.DELETE_ON_ERROR:
GENICE=genice

all: README.md

%: temp_% replacer.py genice_rdf/formats/_RDF.py
	python replacer.py < $< > $@


test: 5.rdf.test
%.rdf: genice_rdf/formats/_RDF.py Makefile
	$(GENICE) $* -r 3 3 3 -w tip4p -f _RDF[H=HW1=HW2,OW] --debug > $@
%.test:
	make $*
	diff $* ref/$*
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
