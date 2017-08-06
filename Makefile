clean:
	rm -f dist/*.tar.gz
	rm -f dist/*.whl
	rm -f dist/*.egg
	rm -rf build

build:
	python setup.py sdist bdist_wheel

upload: build
	twine upload dist/*

test:
	flake8

.PHONY: clean build upload
