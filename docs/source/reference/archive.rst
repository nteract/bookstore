Archiving
=========

.. module:: bookstore.archive

The ``archive`` module
----------------------

The ``archive`` module manages archival of notebooks to storage (i.e. S3) when
a notebook save occurs.

``ArchiveRecord``
~~~~~~~~~~~~~~~~~

Bookstore uses an immutable ``ArchiveRecord`` to represent a notebook file by
its storage path.

.. autoclass:: ArchiveRecord
   :members:


``BookstoreContentsArchiver``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: BookstoreContentsArchiver
   :members:
