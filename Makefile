help:
	@echo "\033]0;suite\007"
	@echo "\n\033[1m------ suite ------\033[0m \n\
	\033[1mopen\033[0m: opens project in sublime\n\
	\033[1mtest\033[0m: run unit testing\n\
	\033[1mdeploy\033[0m: tag upload\n\n\
	\t \033[94mhttps://github.com/stevepeak/suite\033[0m\n\
	\t\t\033[91mHappy Hacking\033[0m\n"

open:
	subl --project ./suite.sublime-project

deploy: tag upload

tag:
	git tag -m "" -a v$(shell grep "version = '" suite/__init__.py | cut -d"'" -f 2)
	git push origin v$(shell grep "version = '" suite/__init__.py | cut -d"'" -f 2)

upload:
	python setup.py sdist upload

test:
	python -m suite.tests

test.all:
	python2.7 -m suite.tests
	python3.3 -m suite.tests
