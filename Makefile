SHELL := /bin/bash

test:
	time pytest tests

bench_parser:
	time pytest tests/test_parser_pure_openfoam_cases.py

black:
	black -l 82 src tests doc dev

isort:
	isort src tests doc dev

format: black isort
