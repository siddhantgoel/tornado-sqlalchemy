POETRY=poetry run

fmt-black:
	$(POETRY) black examples/ tornado_sqlalchemy/ tests/

lint: lint-black lint-flake8

lint-black:
	$(POETRY) black --check examples/ tornado_sqlalchemy/ tests/

lint-flake8:
	$(POETRY) flake8

test: test-pytest

test-pytest:
	$(POETRY) py.test tests/

.PHONY: lint-black lint-flake8 lint\
	test-pytest test
