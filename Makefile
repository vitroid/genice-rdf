.DELETE_ON_ERROR:
GENICE=genice2
BASE=genice2_rdf
PACKAGE=genice2-rdf
all: README.md

%: temp_% replacer.py $(BASE)/formats/_RDF.py
	pip install genice2-dev
	python3 replacer.py < $< > $@


test: 5.rdf.test 3.rdf.json.test
%.rdf: $(BASE)/formats/_RDF.py Makefile
	( cd $(BASE) && $(GENICE) $* -r 3 3 3 -w tip4p -f _RDF[H=HW1=HW2:O=OW] --debug ) > $@
%.rdf.json: $(BASE)/formats/_RDF.py Makefile
	( cd $(BASE) && $(GENICE) $* -r 3 3 3 -w tip4p -f _RDF[H=HW1=HW2:O=OW:json] ) > $@
%.test:
	make $*
	diff $* ref/$*


prepare: # might require root privilege.
	pip install genice2 pairlist


test-deploy: build
	twine upload -r pypitest dist/*
test-install:
	pip install pairlist
	pip install --index-url https://test.pypi.org/simple/ $(PACKAGE)



install:
	./setup.py install
uninstall:
	-pip uninstall -y $(PACKAGE)
build: README.md $(wildcard $(BASE)/formats/*.py)
	./setup.py sdist bdist_wheel


deploy: build
	twine upload dist/*
check:
	./setup.py check
clean:
	-rm $(ALL) *~ */*~ *.rdf *.json
	-rm -rf build dist *.egg-info
	-find . -name __pycache__ | xargs rm -rf
