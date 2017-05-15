.PHONY: install
install:
	@python setup.py develop

.PHONY: pep8
pep8:
	@flake8 flasgger --ignore=F403

.PHONY: test
test: pep8
	@py.test tests -s -vv --cov --cov-config=.coveragerc --doctest-modules flasgger

.PHONY: sdist
sdist: test
	@python setup.py sdist bdist_wheel upload

.PHONY: clean
clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
