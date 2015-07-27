.PHONY: run
run:
	python examples/example.py

.PHONY: install
install:
	python setup.py develop

.PHONY: pep8
pep8:
	@flake8 . --ignore=F403

.PHONY: sdist
sdist: pep8
	@python setup.py sdist upload

.PHONY: clean
clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
