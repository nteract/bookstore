# Change Log

## 2.3.0 [Unreleased](https://github.com/nteract/bookstore/compare/2.2.1...HEAD)

## [2.3.0](https://github.com/nteract/bookstore/releases/tag/2.3.0) 2019-07-02

The following 6 authors contributed X commits.

* Carol Willing
* Kyle Kelley
* M Pacer
* Matthew Seal
* Safia Abdalla
* Shelby Sturgis

The full list of changes they made can be seen [on GitHub](https://github.com/nteract/bookstore/issues?q=milestone%3A2.3.0)

### Significant changes

#### New Publishing endpoint

Previously our publishing endpoint was `/api/bookstore/published`, it is now `/api/bookstore/publish`.

#### Cloning

As of 2.3.0 cloning from S3 is now enabled by default.

Cloning allows access to multiple buckets, but you will need to have your configuration set up for any such bucket.

#### Massive Testing improvements

We have built out a framework for unit-testing Tornado handlers. In addition, we have added a collection of unit tests that bring us to a coverage level in non-experimental code of well over 80%.

#### `/api/bookstore/`: Features and Versions

You can identify which features have been enabled and which version of bookstore is available by using the `/api/bookstore` endpoint.

#### REST API Documentation

All APIs are now documented at our [REST API docs](https://bookstore.readthedocs.io/en/latest/openapi.html) using the OpenAPI spec.

#### Clients (Experimental Feature)

In order to enable access to bookstore publishing and cloning we have created a Notebook and Bookstore clients. *This is not well-tested* functionality at the moment, so we discourage its use in production.
It relies on an assumption that a single kernel is attached to a single notebook, and will break if you use multiple notebooks attached to the same kernel.

However, for those who wish to experiment, it offers some fun ways of exploring bookstore.

For example, if you were to run a notebook from within the top-level [bookstore/ci](https://github.com/nteract/bookstore/tree/master/ci) directory while running the integration test server with `yarn test:server` (see more about [local integration testing](https://bookstore.readthedocs.io/en/latest/project/local_ci.html)).
You should be able to publish from inside a notebook using the following code snippet.

```python
from bookstore.client import BookstoreClient
book_store = BookstoreClient()
book_store.publish()
```

And if you have published your notebook to the local ci (e.g., publishing `my_notebook.ipynb` to the minio `bookstore` bucket with the `ci-published` published prefix), you can clone it from S3 using:

```python
from bookstore.client import BookstoreClient
book_store = BookstoreClient()
book_store.clone("bookstore", "ci-published/my_notebook.ipynb")
```

## Releases prior to 2.3.0

[2.2.1 (2019-02-03)](https://github.com/nteract/bookstore/releases/tag/2.2.1)

[2.2.0 (2019-01-29)](https://github.com/nteract/bookstore/releases/tag/2.2.0)

[2.1.0 (2018-11-20)](https://github.com/nteract/bookstore/releases/tag/2.1.0)

[2.0.0 (2018-11-13)](https://github.com/nteract/bookstore/releases/tag/2.0.0)

[0.1 (2018=10-16)](https://github.com/nteract/bookstore/releases/tag/0.1)
