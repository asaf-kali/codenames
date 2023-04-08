PYTHON_TEST_COMMAND=pytest
DEL_COMMAND=gio trash
LINE_LENGTH=120
.PHONY: build

# Install

upgrade-pip:
	pip install --upgrade pip

install-run: upgrade-pip
	pip install -r requirements.txt

install-test:
	pip install -r requirements-dev.txt
	@make install-run --no-print-directory

install-lint:
	pip install -r requirements-lint.txt

install-dev: install-lint install-test
	pre-commit install

install: install-dev lint cover

# Test

test:
	python -m $(PYTHON_TEST_COMMAND)

cover:
	coverage run -m $(PYTHON_TEST_COMMAND)
	coverage html
	xdg-open htmlcov/index.html &
	$(DEL_COMMAND) .coverage*

# Packaging

build:
	$(DEL_COMMAND) -f dist/*
	python -m build

upload-test:
	twine upload --repository testpypi dist/*

upload:
	twine upload dist/*

build-and-upload: build upload

# Lint

format:
	ruff . --fix
	black .
	isort .

check-ruff:
	ruff .

check-black:
	black --check .

check-isort:
	isort --check .

check-mypy:
	mypy .

check-pylint:
	pylint codenames/ --fail-under=10

lint: format
	pre-commit run --all-files
	@make check-pylint --no-print-directory
