VERSION = $(shell awk '/^Version: / { match($$0, /^Version: /); print substr($$0, RLENGTH + 1) }' steeve.egg-info/PKG-INFO)

.PHONY: test
test:
	@cd tests; PYTHONPATH=.. py.test --tb=short

.PHONY: bdist_deb
bdist_deb:
	python setup.py --command-packages=stdeb.command sdist_dsc
	cd deb_dist/steeve-$(VERSION) \
		&& cp ../../debian/changelog debian \
		&& dpkg-buildpackage -rfakeroot -uc -us
