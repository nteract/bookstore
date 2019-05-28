Usage
=====

Data scientists and notebook users may develop locally on their system or save
their notebooks to off-site or cloud storage. Additionally, they will often
create a notebook and then over time make changes and update it. As they work,
it's helpful to be able to **store versions** of a notebook. When making changes
to the content and calculations over time, a data scientist using Bookstore can
now request different versions from the remote storage, such as S3, and
**clone** the notebook to their local system.

.. note:: **store and clone**

    *store*

    User saves to Local System ------------------> Remote Data Store (i.e. S3)


    *clone*

    User requests a notebook to use locally <-------------- Remote Data Store (i.e. S3)


After some time working with a notebook, the data scientist may want to save or
share a polished notebook version with others. By **publishing a notebook**, the
data scientist can display and share work that others can use at a later time.

How to store and clone versions
-------------------------------

Bookstore uses automatic notebook version management and specific storage paths
when storing a notebook.

Automatic notebook version management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every *save* of a notebook creates an *immutable copy* of the notebook on object
storage. Initially, Bookstore supports S3 for object storage.

To simplify implementation and management of versions, we currently rely on S3
as the object store using `versioned buckets
<https://docs.aws.amazon.com/AmazonS3/latest/dev/Versioning.html>`_. When a
notebook is saved, it overwrites the existing file in place using the versioned
s3 buckets to handle the versioning.

Storage paths
~~~~~~~~~~~~~

All notebooks are archived to a single versioned S3 bucket using specific
**prefixes** to denote a user's workspace and an organization's publication of a
user's notebook. This captures the lifecycle of the notebook on storage. To do
this, bookstore allows users to set workspace and published storage paths. For
example:

- ``/workspace`` - where users edit and store notebooks
- ``/published`` - notebooks to be shared to an organization

Bookstore archives notebook versions by keeping the path intact (until a user
changes them). For example, the prefixes that could be associated with storage
types:

- Notebook in "draft" form: ``/workspace/kylek/notebooks/mine.ipynb``
- Most recent published copy of a notebook: ``/published/kylek/notebooks/mine.ipynb``

.. note:: *Scheduling (Planned for a future release)*

    When scheduling execution of notebooks, each notebook path is a namespace
    that an external service can access. This helps when working with
    parameterized notebooks, such as with Papermill. Scheduled notebooks may
    also be referred to by the notebook ``key``. In addition, Bookstore can
    find version IDs as well.

Easing the transition to Bookstore's storage plan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since many people use a regular filesystem, we'll start with writing to the
``/workspace`` prefix as Archival Storage (more specifically, writing on save
using a ``post_save_hook`` for the Jupyter contents manager).

How to publish a notebook
-------------------------

To publish a notebook, Bookstore uses a publishing endpoint which is a
``serverextension`` to the classic Jupyter server. If you wish to publish
notebooks, explicitly enable bookstore as a server extension to use the
endpoint. By default, publishing is not enabled.

To enable the extension globally, run::

    jupyter serverextension enable --py bookstore

If you wish to enable it only for your current environment, run::

    jupyter serverextension enable --py bookstore --sys-prefix
