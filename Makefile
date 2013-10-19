.POSIX:

PYTHON=python
DOCTARGET=html

check:
	PYTHONPATH=$(PWD) $(PYTHON) test/test_ihih.py

egg: clean
	$(PYTHON) setup.py sdist bdist_egg

doc:
	cd docs && $(MAKE) $(DOCTARGET)

install:
	$(PYTHON) setup.py install

installcheck: check install

clean:
	rm -rf *.py? build dist ihih.egg-info
	cd docs && $(MAKE) $@
