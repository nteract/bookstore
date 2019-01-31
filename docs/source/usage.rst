Usage
=====

Automatic Notebook Versioning
-----------------------------

Every *save* of a notebook creates an *immutable copy* of the notebook on object storage.

To simplify implementation, we currently rely on S3 as the object store, using
`versioned buckets <https://docs.aws.amazon.com/AmazonS3/latest/dev/Versioning.html>`_.

Storage Paths
-------------

All notebooks are archived to a single versioned S3 bucket with specific **prefixes** denoting the lifecycle of
the notebook. For example:

- ``/workspace`` - where users edit
- ``/published`` - public notebooks (to an organization)

Each notebook path is a namespace that an external service ties into the schedule. We archive off versions,
keeping the path intact (until a user changes them). For example, the prefixes that could be associated with
storage types:

- Notebook in "draft" form: ``/workspace/kylek/notebooks/mine.ipynb``
- Most recent published copy of a notebook: ``/published/kylek/notebooks/mine.ipynb``

Scheduled notebooks will also be referred to by the notebook ``key``. In addition, we'll need to be able to surface
version IDs as well.

Transitioning to this Storage Plan
----------------------------------

Since most people are on a regular filesystem, we'll start with writing to the `/workspace` prefix as Archival
Storage (writing on save using a ``post_save_hook`` for a Jupyter contents manager).

Publishing
----------

The bookstore publishing endpoint is a ``serverextension`` to the classic Jupyter server. This means if you are
developing this you will need to explicitly enable it to use the endpoint.

To do so you run: ``jupyter serverextension enable --py bookstore``.

If you wish to enable it only for your current environment, run:

``jupyter serverextension enable --py bookstore --sys-prefix``.
