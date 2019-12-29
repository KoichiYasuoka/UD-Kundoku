#! /bin/sh
rm -fr build dist udkundoku.egg-info
python3 setup.py sdist
git status
twine upload --repository pypi dist/*
exit 0
