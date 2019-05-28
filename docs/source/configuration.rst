Configuration
=============

Commonly used configuration settings can be stored in ``BookstoreSettings`` in the
``jupyter_notebook_config.py`` file. These settings include:

    - workspace location
    - published storage location
    - S3 bucket information
    - AWS credentials for S3

Example configuration
---------------------

Here's an example of ``BookstoreSettings`` in the ``~/.jupyter/jupyter_notebook_config.py`` file:

.. code-block:: python

    """jupyter notebook configuration
    The location for user installs on MacOS is ``~/.jupyter/jupyter_notebook_config.py``.
    See https://jupyter.readthedocs.io/en/latest/projects/jupyter-directories.html for additional locations.
    """
    from bookstore import BookstoreContentsArchiver


    c.NotebookApp.contents_manager_class = BookstoreContentsArchiver

    c.BookstoreSettings.workspace_prefix = "/workspace/kylek/notebooks"
    c.BookstoreSettings.published_prefix = "/published/kylek/notebooks"

    c.BookstoreSettings.s3_bucket = "<bucket-name>"

    # If bookstore uses an EC2 instance with a valid IAM role, there is no need to specify here
    c.BookstoreSettings.s3_access_key_id = <AWS Access Key ID / IAM Access Key ID>
    c.BookstoreSettings.s3_secret_access_key = <AWS Secret Access Key / IAM Secret Access Key>


The root directory of bookstore's GitHub repo contains an example config
called ``jupyter_config.py.example`` that shows how to configure
``BookstoreSettings``.
