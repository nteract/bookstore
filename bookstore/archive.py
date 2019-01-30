"""Archival of notebooks"""
import json
from asyncio import Lock
from typing import Dict, NamedTuple

import aiobotocore
from notebook.services.contents.filemanager import FileContentsManager
from tornado import ioloop

from .bookstore_config import BookstoreSettings
from .s3_paths import s3_key, s3_display_path


class ArchiveRecord(NamedTuple):
    """Representation of archived content"""
    filepath: str
    content: str
    queued_time: float


class BookstoreContentsArchiver(FileContentsManager):
    """Archives notebooks to S3 on save by UI or parameterized workflow

    Bookstore settings and Jupyter application settings are shared
    A session is created for the current event loop
    To write to a particular path on S3, acquire a path_lock.
    The lock avoids multiple writes contending to write at the same time.

    After acquiring the lock, `archive` authenticates using the storage service's
    credentials. If allowed, the notebook is written to storage (i.e. S3).
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

        # TODO: create a better check for credentials - keys and config or it will fail
        try:
            # create a session object from the current event loop
            self.session = aiobotocore.get_session()
        except Exception as e:
            self.log.error(
                "{} : Check credentials and configuration".format(e)
            )

        # A lock per path to suppress writing to S3 when currently writing
        self.path_locks: Dict[str, Lock] = {}
        # Since locks are not pre-created,
        self.ability_to_create_path_lock = Lock()

    async def archive(self, record: ArchiveRecord):
        """Process a storage write

        Acquire a path lock before archive.
        Writing to storage will only be allowed to a path if there
        is a valid path_lock held and the path is not locked by
        another process.
        """
        async with self.ability_to_create_path_lock:
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
