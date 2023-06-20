SHELL := /bin/bash

test:
	time pytest tests doc/examples -v

bench_parser:
	time pytest tests/test_parser_saved_cases.py

cov:
	time pytest tests doc/examples/ --cov --cov-report term --cov-report html
	@echo "Code coverage analysis complete. View detailed report:"
	@echo "file://${PWD}/htmlcov/index.html"

black:
	black -l 82 src tests doc dev

isort:
	isort src tests doc dev

format: black isort

poetry_install_all:
	poetry install --all-extras
