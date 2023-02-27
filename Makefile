
test:
	pytest tests

black:
	black -l 82 src tests doc

isort:
	isort src tests doc

format: black isort
