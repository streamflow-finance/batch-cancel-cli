.PHONY: coverage
coverage:
	coverage run -m pytest tests
	coverage report -m
	coverage html
	open htmlcov/index.html


.PHONE: lint
lint:
	ruff format cli
	ruff check cli --fix
	mypy cli --namespace-packages --show-absolute-path
