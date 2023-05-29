PYTHON_TEST_COMMAND=pytest
DEL_COMMAND=gio trash
LINE_LENGTH=120
.PHONY: build
SYNC=--sync

# Install

upgrade-pip:
	pip install --upgrade pip

install-ci: upgrade-pip
	pip install poetry==1.4.2
	poetry config virtualenvs.create false

install-run:
	poetry install --only main

install-test:
	poetry install --only main --only test

install-lint:
	poetry install --only lint

install-dev: upgrade-pip
	poetry install --all-extras	$(SYNC)
	pre-commit install

install: lock-check install-dev lint cover

# Poetry

lock:
	poetry lock --no-update

lock-check:
	poetry lock --check

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
	poetry build

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
