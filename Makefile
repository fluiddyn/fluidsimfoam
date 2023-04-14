SHELL := /bin/bash

test:
	time pytest tests

black:
	black -l 82 src tests doc dev

isort:
	isort src tests doc dev

format: black isort
