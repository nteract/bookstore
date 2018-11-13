from notebook.services.contents.filemanager import FileContentsManager

import s3fs

from traitlets import (
    HasTraits,
    Any,
    Bool,
    Dict,
    Instance,
    List,
    TraitError,
    Type,
    Unicode,
    validate,
    default,
    Instance
)

import json

from .bookstore_config import BookstoreSettings

class BookstoreContentsArchiver(FileContentsManager):
    """
    Archives notebooks to S3 on save
    """

    def __init__(self, *args, **kwargs):
        super(FileContentsManager, self).__init__(*args, **kwargs)
        # opt ourselves into being part of the Jupyter App that should have Bookstore Settings applied
        self.settings = BookstoreSettings(parent=self)

        self.log.info("Archiving notebooks to {}".format(self.full_prefix))

        self.fs = s3fs.S3FileSystem(key=self.settings.s3_access_key_id,
                                    secret=self.settings.s3_secret_access_key,
                                    client_kwargs={
                                        "endpoint_url": self.settings.s3_endpoint_url,
                                        "region_name": self.settings.s3_region_name
                                    },
                                    config_kwargs={},
                                    s3_additional_kwargs={})

    @property
    def delimiter(self):
        """It's a slash! Normally this could be configurable. This leaves room for that later,
        keeping it centralized for now"""
        return "/"

    @property
    def full_prefix(self):
        """Full prefix: bucket + workspace prefix"""
        return self.delimiter.join([self.settings.s3_bucket, self.settings.workspace_prefix])

    def s3_path(self, path):
        """compute the s3 path based on the bucket, prefix, and the path to the notebook"""
        return self.delimiter.join([self.full_prefix, path])

    def run_pre_save_hook(self, model, path, **kwargs):
        """Store notebook to S3 when saves happen
        """
        if model['type'] != 'notebook':
            return

        # TODO: store the hash of the notebook to not write on every save
        notebook_contents = json.dumps(model['content'])

        full_path = self.s3_path(path)

        # write to S3
        # TODO: Write to S3 asynchronously to not block other server operations
        with self.fs.open(full_path, mode='wb') as f:
            f.write(notebook_contents.encode('utf-8'))
