# Releasing

First check that the CHANGELOG is up to date for the next release version

```
git tag 2.0.0
git push && git push --tags
rm -rf dist/*
python setup.py sdist bdist_wheel
twine upload dist/*
```
