"""Archival of notebooks"""
import json
import logging
from asyncio import Lock
from typing import Dict, NamedTuple

import aiobotocore
from notebook.services.contents.filemanager import FileContentsManager
from tornado import ioloop

from .bookstore_config import BookstoreSettings
from .s3_paths import s3_key, s3_display_path


class ArchiveRecord(NamedTuple):
    """Representation of content to archive

    A record to be archived is a tuple containing `filepath`, the `content` to
    be archived, and the length of time in queue for archiving (`queued_time`).
    """

    filepath: str
    content: str
    queued_time: float


class BookstoreContentsArchiver(FileContentsManager):
    """Archives notebooks to storage (S3) on notebook save

    This class is a custom Jupyter `FileContentsManager` which holds information
    on storage location, path to it, and file to be written there.

    Bookstore settings combine with the parent Jupyter application settings.
``
    A session is created for the current event loop. To write to a particular
    path on S3, acquire a lock. After acquiring the lock, `archive`
    authenticates using the storage service's credentials. If allowed, the

    notebook is queued to be written to storage (i.e. S3).

    Attributes
    ----------
    path_locks : dict
        Dictionary of paths to storage and the lock associated with a path
    path_lock_ready: ayncio mutex lock
        A mutex lock associated with a path

    See also
    --------
    https://jupyter-notebook.readthedocs.io/en/stable/extending/contents.html#contents-api
    """

    def __init__(self, *args, **kwargs):
        super(FileContentsManager, self).__init__(*args, **kwargs)

        # opt ourselves into being part of the Jupyter App that should have Bookstore Settings applied
        self.settings = BookstoreSettings(parent=self)

        self.log.info(
            "Archiving notebooks to {}".format(
                s3_display_path(self.settings.s3_bucket, self.settings.workspace_prefix)
            )
        )

        try:
            # create a session object from the current event loop
            self.session = aiobotocore.get_session()
        except Exception:
            self.log.warn("Unable to create a session")
            raise

        # a collection of locks per path to suppress writing while the path may be in use
        self.path_locks: Dict[str, Lock] = {}
        self.path_lock_ready = Lock()

    async def archive(self, record: ArchiveRecord):
        """Process a record to write to storage.

        Acquire a path lock before archive. Writing to storage will only be
        allowed to a path if a valid path_lock is held and the path is not
        locked by another process.

        Parameters
        ----------
        record : ArchiveRecord
            A notebook and where it should be written to storage
        """
        async with self.path_lock_ready:
            lock = self.path_locks.get(record.filepath)

            if lock is None:
                lock = Lock()
                self.path_locks[record.filepath] = lock

        # Skip writes when a given path is already locked
        if lock.locked():
            self.log.info("Skipping archive of %s", record.filepath)
            return

        async with lock:
            try:
                async with self.session.create_client(
                    's3',
                    aws_secret_access_key=self.settings.s3_secret_access_key,
                    aws_access_key_id=self.settings.s3_access_key_id,
                    endpoint_url=self.settings.s3_endpoint_url,
                    region_name=self.settings.s3_region_name,
                ) as client:
                    self.log.info("Processing storage write of %s", record.filepath)
                    file_key = s3_key(self.settings.workspace_prefix, record.filepath)
                    await client.put_object(
                        Bucket=self.settings.s3_bucket, Key=file_key, Body=record.content
                    )
                    self.log.info("Done with storage write of %s", record.filepath)
            except Exception as e:
                self.log.error(
                    'Error while archiving file: %s %s', record.filepath, e, exc_info=True
                )

    def run_pre_save_hook(self, model, path, **kwargs):
        """Store notebook to S3 when save occurs

        This hook offloads the storage request to the event loop.
        When the event loop is available for execution of the request, the
        storage of the notebook will be done and the write to storage occurs.

        Parameters
        ----------
        model : str
            The type of file
        path : str
            The storage location
        """
        if model["type"] != "notebook":
            return

        content = json.dumps(model["content"])

        loop = ioloop.IOLoop.current()

        # Offload archival and schedule write to storage with the current event loop
        loop.spawn_callback(
            self.archive,
            ArchiveRecord(
                content=content, filepath=path, queued_time=ioloop.IOLoop.current().time()
            ),
        )
