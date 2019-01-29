# Releasing

## Pre-release

- [ ] First check that the CHANGELOG is up to date for the next release version.

- [ ] Update docs

## Installing twine package

Install and upgrade, if needed,`twine` with `python3 -m pip install -U twine`. 
The long description of the package will not render on PyPI unless an up-to-date
version is used.

## Create the release

- [ ] Update version number `bookstore/_version.py`
- [ ] Commit the updated version
- [ ] Clean the repo of all non-tracked files: `git clean -xdfi`
- [ ] Commit and tag the release

```
git commit -am"release $VERSION"
git tag $VERSION
```
- [ ] Push the tags and remove any existing `dist` directory files

```
git push && git push --tags
rm -rf dist/*
```

- [ ] Build `sdist` and `wheel`

```
python setup.py sdist
python setup.py bdist_wheel
```

## Test and upload release to PyPI

- [ ] Test the wheel and sdist locally
- [ ] Upload to PyPI using `twine` over SSL

```
twine upload dist/*
```

- [ ] If all went well:
  - Change `bookstore/_version.py` back to `.dev`
  - Push directly to `master` and push `--tags` too.