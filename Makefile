.PHONY: run
run:
	python wsgi.py

.PHONY: install
install:
	python setup.py develop

.PHONY: test
test:
	@flake8 . --ignore=F403

.PHONY: sdist
sdist: test
	@python setup.py sdist upload

.PHONY: clean
clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
