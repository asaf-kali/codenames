PYTHON_TEST_COMMAND=pytest
ifeq ($(OS),Windows_NT)
	OPEN_FILE_COMMAND=start
	DEL_COMMAND=del
else
	OPEN_FILE_COMMAND=xdg-open
	DEL_COMMAND=gio trash
endif
SYNC=--sync
.PHONY: build

# Install

upgrade-pip:
	pip install --upgrade pip

install-ci: upgrade-pip
	pip install poetry==1.5.1
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
	$(OPEN_FILE_COMMAND) htmlcov/index.html &
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

# Semantic release

semrel:
	@echo "Releasing version..."
	semantic-release version

semrel-dev:
	@echo "Releasing dev version..."
	semantic-release version --no-commit --no-push
	# Replace "-dev.1" with epoch time in version
	sed -i 's/-dev.1/.dev.$(shell date +%s)/g' pyproject.toml
	make build

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

# Quick and dirty

wip:
	git add .
	git commit -m "Auto commit." --no-verify
	git push

amend:
	git add .
	git commit --amend --no-edit --no-verify
