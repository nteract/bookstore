import json
import aiobotocore

from asyncio import Lock
from typing import Dict, NamedTuple

from notebook.services.contents.filemanager import FileContentsManager
from tornado import ioloop

from .bookstore_config import BookstoreSettings

from .s3_paths import s3_key, s3_display_path


class ArchiveRecord(NamedTuple):
    filepath: str
    content: str
    queued_time: float


class BookstoreContentsArchiver(FileContentsManager):
    """
    Archives notebooks to S3 on save
    """

    def __init__(self, *args, **kwargs):
        super(FileContentsManager, self).__init__(*args, **kwargs)
        # opt ourselves into being part of the Jupyter App that should have Bookstore Settings applied
        self.settings = BookstoreSettings(parent=self)

        self.log.info("Archiving notebooks to {}".format(s3_display_path(
            self.settings.s3_bucket, self.settings.workspace_prefix)))

        self.session = aiobotocore.get_session()

        # A lock per path to suppress writing to S3 when currently writing
        self.path_locks: Dict[str, Lock] = {}
        # Since locks are not pre-created,
        self.ability_to_create_path_lock = Lock()

    async def archive(self, record: ArchiveRecord):
        """Process a storage write, only allowing one write at a time to each path
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
                async with self.session.create_client('s3',
                                                      aws_secret_access_key=self.settings.s3_secret_access_key,
                                                      aws_access_key_id=self.settings.s3_access_key_id,
                                                      endpoint_url=self.settings.s3_endpoint_url,
                                                      region_name=self.settings.s3_region_name,
                                                      ) as client:
                    self.log.info("Processing storage write of %s", record.filepath)
                    file_key = s3_key(self.settings.workspace_prefix, record.filepath)
                    await client.put_object(Bucket=self.settings.s3_bucket, Key=file_key, Body=record.content)
                    self.log.info("Done with storage write of %s", record.filepath)
            except Exception as e:
                    self.log.error(
                        'Error while archiving file: %s %s',
                        record.filepath,
                        e,
                        exc_info=True,
                    )

    def run_pre_save_hook(self, model, path, **kwargs):
        """Store notebook to S3 when saves happen
        """
        if model["type"] != "notebook":
            return

        content = json.dumps(model["content"])

        loop = ioloop.IOLoop.current()

        # Offload the archival to be scheduled to work on the event loop
        loop.spawn_callback(
            self.archive,
            ArchiveRecord(
                content=content,
                filepath=path,
                queued_time=ioloop.IOLoop.current().time(),
            ),
        )
