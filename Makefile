.PHONY: tag test

open:
	subl --project ./dictime.sublime-project

deploy: tag upload

tag:
	git tag -m "" -a v$(shell grep "VERSION = '" dictime/__init__.py | cut -d"'" -f 2)
	git push origin v$(shell grep "VERSION = '" dictime/__init__.py | cut -d"'" -f 2)

upload:
	python setup.py sdist upload

test:
	. venv/bin/activate; nosetests --with-coverage --cover-package=dictime --cover-html --cover-html-dir=coverage_html_report --cover-branches

test.all:
	python2.7 -m dictime.tests
	python3.3 -m dictime.tests

venv:
	virtualenv venv
	. venv/bin/activate; pip install nose rednose coverage
	. venv/bin/activate; pip install -r requirements.txt
