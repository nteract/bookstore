"""Archival of notebooks"""

import json
from asyncio import Lock
from typing import Dict
from typing import NamedTuple

import aiobotocore
from notebook.services.contents.filemanager import FileContentsManager
from tornado import ioloop

from .bookstore_config import BookstoreSettings
from .s3_paths import s3_key, s3_display_path


class ArchiveRecord(NamedTuple):
    """Represents an archival record.

    An `ArchiveRecord` uses a Typed version of `collections.namedtuple()`. The
    record is immutable.

    Example
    -------

    An archive record (`filepath`, `content`, `queued_time`) contains:

    - a `filepath` to the record
    - the `content` for archival
    - the `queued time` length of time waiting in the queue for archiving
    """

    filepath: str
    content: str
    queued_time: float  # TODO: refactor to a datetime time


class BookstoreContentsArchiver(FileContentsManager):
    """Manages archival of notebooks to storage (S3) when notebook save occurs.

    This class is a custom Jupyter
    `FileContentsManager <https://jupyter-notebook.readthedocs.io/en/stable/extending/contents.html#contents-api>`_
    which holds information on storage location, path to it, and file to be
    written.

    Example
    -------

    - Bookstore settings combine with the parent Jupyter application settings.
    - A session is created for the current event loop.
    - To write to a particular path on S3, acquire a lock.
    - After acquiring the lock, `archive` method authenticates using the storage
      service's credentials.
    - If allowed, the notebook is queued to be written to storage (i.e. S3).

    Attributes
    ----------

    path_locks : dict
        Dictionary of paths to storage and the lock associated with a path.
    path_lock_ready: asyncio mutex lock
        A mutex lock associated with a path.
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
        allowed to a path if a valid `path_lock` is held and the path is not
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
        """Send request to store notebook to S3.

        This hook offloads the storage request to the event loop.
        When the event loop is available for execution of the request, the
        storage of the notebook will be done and the write to storage occurs.

        Parameters
        ----------

        model : dict
            The type of file and its contents
        path : str
            The storage location
        """
        if model["type"] != "notebook":
            self.log.debug(
                "Bookstore only archives notebooks, "
                f"request does not state that {path} is a notebook."
            )
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
