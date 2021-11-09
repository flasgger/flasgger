.PHONY: install
install:
	@python setup.py develop

.PHONY: pep8
pep8:
	@flake8 flasgger --ignore=F403

.PHONY: flasgger_package
flasgger_package:
	@cd etc/flasgger_package; python setup.py install

.PHONY: test
test: pep8 flasgger_package
	@py.test tests -s -vv --cov --cov-config=.coveragerc --doctest-modules flasgger

.PHONY: sdist
sdist: test
	@rm -rf dist/*
	@python setup.py sdist bdist_wheel
	@twine upload dist/*

.PHONY: clean
clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;

# Updates swagger_ui_dist files
# Need to manually remove extra files added by this command
upgrade_swagger_ui:
	@tar --strip-components 1 -C flasgger/ui3/static/ -xvf `npm pack swagger-ui-dist@3.28.0` package/
