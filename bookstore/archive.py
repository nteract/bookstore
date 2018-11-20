import json
from asyncio import Lock
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, NamedTuple

import s3fs
from notebook.services.contents.filemanager import FileContentsManager
from tornado import gen, ioloop
from tornado.concurrent import run_on_executor
from tornado.util import TimeoutError

from .bookstore_config import BookstoreSettings


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

        self.log.info("Archiving notebooks to {}".format(self.full_prefix))

        self.fs = s3fs.S3FileSystem(
            key=self.settings.s3_access_key_id,
            secret=self.settings.s3_secret_access_key,
            client_kwargs={
                "endpoint_url": self.settings.s3_endpoint_url,
                "region_name": self.settings.s3_region_name,
            },
            config_kwargs={},
            s3_additional_kwargs={},
        )

        self._thread_pool = ThreadPoolExecutor(max_workers=self.settings.max_threads)

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
                self.log.info("Processing storage write of %s", record.filepath)
                full_path = self.s3_path(record.filepath)
                await self.write_to_s3(full_path, record.content)
                self.log.info("Done with storage write of %s", record.filepath)
            except Exception as e:
                self.log.error(
                    'Error while archiving file: %s %s',
                    record.filepath,
                    e,
                    exc_info=True,
                )

    @run_on_executor(executor='_thread_pool')
    def write_to_s3(self, full_path: str, content: str):
        with self.fs.open(full_path, mode="wb") as f:
            f.write(content.encode("utf-8"))

    @property
    def delimiter(self):
        """It's a slash! Normally this could be configurable. This leaves room for that later,
        keeping it centralized for now"""
        return "/"

    @property
    def full_prefix(self):
        """Full prefix: bucket + workspace prefix"""
        return self.delimiter.join(
            [self.settings.s3_bucket, self.settings.workspace_prefix]
        )

    def s3_path(self, path):
        """compute the s3 path based on the bucket, prefix, and the path to the notebook"""
        return self.delimiter.join([self.full_prefix, path])

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
