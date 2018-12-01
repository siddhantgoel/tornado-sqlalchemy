update-deps:
	pip-compile requirements.in > requirements.txt
	pip-compile requirements.dev.in > requirements.dev.txt

install-deps:
	pip install -r requirements.txt
	pip install -r requirements.dev.txt

.PHONY: update-deps install-deps
