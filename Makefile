default: m

clean: clean-build clean-pyc clean-installer
c: clean

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	rm -f .coverage
	rm -f *.log

clean-installer:
	rm -fr output/
	rm -fr app.spec
	rm -f narfecritters.spec
	rm -f narfecritters.zip

clean-pyc: ## remove Python file artifacts
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*~' -exec rm -f {} +

data-pull:
	cd data && git pull

data-push:
	cd data && git push origin

init:
	pip install -r .

init-dev:
	pip install -r requirements_test.txt

pyinstaller: clean
	pyinstaller --noconfirm --onefile --windowed \
		-n narfecritters --uac-admin \
		app.py
	rsync -av --exclude='.git' data dist/
	cp README.* dist/
	7z a narfecritters.zip dist/*
	7z rn narfecritters.zip dist narfecritters

run-main:
	python -m narfecritters.main

run-test:
	pytest --cov=narfecritters --cov-report term-missing tests/

release-test: clean
	python setup.py sdist bdist_wheel
	twine upload --repository pypitest dist/*

release-prod: clean
	python setup.py sdist bdist_wheel
	twine upload --repository pypi dist/*

release: run-test release-test release-prod clean

m: run-main
main: init m
t: run-test
test: init-dev t
