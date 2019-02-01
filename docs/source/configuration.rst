Configuration
=============


Bookstore settings in Jupyter configuration file
------------------------------------------------

``BookstoreSettings`` can store commonly used settings for
bookstore. These settings include:

    - the workspace and published storage location
    - S3 bucket information
    - AWS credentials for S3 may also be addeds

Examples
~~~~~~~~

What follows is an example of this in the ``~/.jupyter/jupyter_notebook_config.py`` file:

.. code-block:: python

    """jupyter config
    # At ~/.jupyter/jupyter_notebook_config.py for user installs on macOS
    # See https://jupyter.readthedocs.io/en/latest/projects/jupyter-directories.html for other places to plop this
    """
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


An example of using BookstoreSettings in the ``~/jupyter/jupyter_config.py`` file can be found in the root directory
of bookstore's GitHub repo.