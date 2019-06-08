Configuration
=============

Bookstore may be configured by providing ``BookstoreSettings`` in the
``~/.jupyter/jupyter_notebook_config.py`` file.

The ``bookstore_config`` module
-------------------------------

.. module:: bookstore.bookstore_config

``BookstoreSettings``
~~~~~~~~~~~~~~~~~~~~~

These settings are configurable by the user. Bookstore uses the traitlets
library to handle the configurable options.

.. autoclass:: BookstoreSettings
   :members:

Functions
~~~~~~~~~

These functions will generally be used by developers of the bookstore application.

.. autofunction:: validate_bookstore