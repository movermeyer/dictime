.PHONY: tag test

open:
	subl --project ./suite.sublime-project

deploy: tag upload

tag:
	git tag -m "" -a v$(shell grep "version = '" suite/__init__.py | cut -d"'" -f 2)
	git push origin v$(shell grep "version = '" suite/__init__.py | cut -d"'" -f 2)

upload:
	python setup.py sdist upload

test:
	. venv/bin/activate; nosetests --with-coverage --cover-package=suite --cover-html --cover-html-dir=coverage_html_report --cover-branches

test.all:
	python2.7 -m suite.tests
	python3.3 -m suite.tests

venv:
	virtualenv venv
	. venv/bin/activate; pip install nose rednose coverage
	. venv/bin/activate; pip install -r requirements.txt
