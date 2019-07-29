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


prepare: # might require root privilege.
	pip install genice pairlist


test-deploy: build
	twine upload -r pypitest dist/*
test-install:
	pip install pairlist
	pip install --index-url https://test.pypi.org/simple/ genice-rdf



install:
	./setup.py install
uninstall:
	-pip uninstall -y genice-rdf
build: README.md $(wildcard genice_rdf/formats/*.py)
	./setup.py sdist bdist_wheel


deploy: build
	twine upload dist/*
check:
	./setup.py check
pypi: check
	./setup.py sdist bdist_wheel upload
clean:
	-rm $(ALL) *~ */*~ *.rdf
	-rm -rf build dist *.egg-info
	-find . -name __pycache__ | xargs rm -rf
