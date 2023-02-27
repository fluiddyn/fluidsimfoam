
test:
	pytest tests

black:
	black -l 82 src tests doc
