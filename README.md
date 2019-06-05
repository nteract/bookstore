# bookstore :books:

[![Documentation Status](https://readthedocs.org/projects/bookstore/badge/?version=latest)](https://bookstore.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/nteract/bookstore.svg?branch=master)](https://travis-ci.org/nteract/bookstore)
[![CircleCI](https://circleci.com/gh/nteract/bookstore.svg?style=shield)](https://circleci.com/gh/nteract/bookstore)
[![Codecov](https://codecov.io/gh/nteract/bookstore/branch/master/graph/badge.svg)](https://codecov.io/gh/nteract/bookstore)

**bookstore** :books: provides tooling and workflow recommendations for storing :cd:, scheduling :calendar:, and publishing :book: notebooks.

The full documentation is hosted on [ReadTheDocs](https://bookstore.readthedocs.io).

## How does bookstore work

### Automatic Notebook Versioning

Every *save* of a notebook creates an *immutable copy* of the notebook on object storage.

To simplify implementation, we currently rely on S3 as the object store, using [versioned buckets](https://docs.aws.amazon.com/AmazonS3/latest/dev/Versioning.html).

<!--

Include diagram for versioning

-->

### Storage Paths

All notebooks are archived to a single versioned S3 bucket with specific prefixes denoting the lifecycle of the notebook:

- `/workspace` - where users edit
- `/published` - public notebooks (to an organization)

Each notebook path is a namespace that an external service ties into the schedule. We archive off versions, keeping the path intact (until a user changes them).

| Prefix                                  | Intent                 |
|-----------------------------------------|------------------------|
| `/workspace/kylek/notebooks/mine.ipynb` | Notebook in “draft”    |
| `/published/kylek/notebooks/mine.ipynb` | Current published copy |

Scheduled notebooks will also be referred to by the notebook key. In addition, we'll need to be able to surface version IDs as well.

### Transitioning to this Storage Plan

Since most people are on a regular filesystem, we'll start with writing to the
`/workspace` prefix as Archival Storage (writing on save using a `post_save_hook`
for a Jupyter contents manager).

### Publishing

The bookstore publishing endpoint is a `serverextension` to the classic Jupyter
server. This means you will need to explicitly enable the `serverextension`
to use the endpoint.

To do so, run:

    jupyter serverextension enable --py bookstore

To enable it only for the current environment, run:

    jupyter serverextension enable --py bookstore --sys-prefix

## Installation

**bookstore** requires Python 3.6 or higher.

Note: Supports installation on Jupyter servers running Python 3.6 and above.
Your notebooks can still be run in Python 2 or Python 3.

1. Clone this repo.
2. At the repo's root, enter in the Terminal: `python3 -m pip install .` (Tip: don't forget the dot at the end of the command)

## Configuration

```python
# jupyter config
# At ~/.jupyter/jupyter_notebook_config.py for user installs on macOS
# See https://jupyter.readthedocs.io/en/latest/projects/jupyter-directories.html for other places to plop this

from bookstore import BookstoreContentsArchiver

c.NotebookApp.contents_manager_class = BookstoreContentsArchiver

# All Bookstore settings are centralized on one config object so you don't have to configure it for each class
c.BookstoreSettings.workspace_prefix = "/workspace/kylek/notebooks"
c.BookstoreSettings.published_prefix = "/published/kylek/notebooks"

c.BookstoreSettings.s3_bucket = "<bucket-name>"

# Note: if bookstore is used from an EC2 instance with the right IAM role, you don't
# have to specify these
c.BookstoreSettings.s3_access_key_id = <AWS Access Key ID / IAM Access Key ID>
c.BookstoreSettings.s3_secret_access_key = <AWS Secret Access Key / IAM Secret Access Key>
```

## Developing

If you are developing on bookstore you will want to run the ci tests locally and to make releases.

Use [CONTRIBUTING.md](./CONTRIBUTING.md) to learn more about contributing.
Use [running_ci_locally.md](./running_ci_locally.md) to learn more about running ci tests locally.
Use [running_python_tests.md](./running_python_tests.md) to learn about running tests locally.
Use [RELEASING.md](./RELEASING.md) to learn more about releasing bookstore.
