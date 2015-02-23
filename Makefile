RAWVERSION = $(filter-out __version__ = , $(shell grep __version__ access_caltech_home/__init__.py))
VERSION = $(strip $(shell echo $(RAWVERSION)))

PACKAGE = shotalizer
FULLPACKAGE = $(PACKAGE)-$(VERSION).tar.gz
SPECFILE = $(PACKAGE).spec
ARCH = $(shell arch)

#======================================================================


clean:
	rm -rf *.tar.gz dist *.egg-info *.rpm build
	find . -name "*.pyc" -exec rm '{}' ';'

dist: clean
	@python setup.py sdist

rpm-butler-rhel6: dist
	cp dist/$(FULLPACKAGE) SOURCES; cp $(SPECFILE) SPECS
	cd SPECS; rpmbuild -ba $(SPECFILE) --define '__version $(VERSION)' --define '_topdir $(TOPDIR)'

rpm-aws: dist
	cp dist/$(FULLPACKAGE) SOURCES; cp $(SPECFILE) SPECS
	cd SPECS; rpmbuild -ba $(SPECFILE) --define '__version $(VERSION)' --define 'amzn64 1' --define '_topdir $(TOPDIR)'
