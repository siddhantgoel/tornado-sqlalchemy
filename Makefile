update-deps:
	pip-compile requirements.dev.in > requirements.dev.txt

install-deps:
	pip install -r requirements.dev.txt

.PHONY: update-deps install-deps
