test:
	nosetests tests --tc-file=tests/.testconfig.yaml --tc-format=yaml --with-id -v
lint:
	flake8 --ignore=F401 bluew
	pylint --rcfile=.pylintrc --notes=FIXME bluew
publish:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*
	rm -rf build dist .egg bluew.egg-info
docs:
	cd docs && make html
