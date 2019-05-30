import json

import aiobotocore
from notebook.base.handlers import APIHandler, path_regex
from tornado import web

from .bookstore_config import BookstoreSettings
from .s3_paths import s3_path
from .s3_paths import s3_key
from .s3_paths import s3_display_path
from .utils import url_path_join


class BookstorePublishHandler(APIHandler):
    """Publish a notebook to the publish path"""

    def initialize(self):
        """Initialize a helper to get bookstore settings and session information quickly"""
        self.bookstore_settings = BookstoreSettings(config=self.config)
        self.session = aiobotocore.get_session()

    @web.authenticated
    async def put(self, path):
        """Publish a notebook on a given path.

        The payload directly matches the contents API for PUT.
        """
        self.log.info("Attempt publishing to %s", path)

        if path == '' or path == '/':
            raise web.HTTPError(400, "Must provide a path for publishing")

        model = self.get_json_body()
        if model:
            await self._publish(model, path.lstrip('/'))
        else:
            raise web.HTTPError(400, "Cannot publish an empty model")

    async def _publish(self, model, path):
        """Publish notebook model to the path"""
        if model['type'] != 'notebook':
            raise web.HTTPError(400, "bookstore only publishes notebooks")
        content = model['content']

        full_s3_path = s3_path(
            self.bookstore_settings.s3_bucket, self.bookstore_settings.published_prefix, path
        )
        s3_object_key = s3_key(self.bookstore_settings.published_prefix, path)

        self.log.info(
            "Publishing to %s",
            s3_display_path(
                self.bookstore_settings.s3_bucket, self.bookstore_settings.published_prefix, path
            ),
        )

        async with self.session.create_client(
            's3',
            aws_secret_access_key=self.bookstore_settings.s3_secret_access_key,
            aws_access_key_id=self.bookstore_settings.s3_access_key_id,
            endpoint_url=self.bookstore_settings.s3_endpoint_url,
            region_name=self.bookstore_settings.s3_region_name,
        ) as client:
            self.log.info("Processing published write of %s", path)
            obj = await client.put_object(
                Bucket=self.bookstore_settings.s3_bucket,
                Key=s3_object_key,
                Body=json.dumps(model['content']),
            )
            self.log.info("Done with published write of %s", path)

        self.set_status(201)

        resp_content = {"s3path": full_s3_path}

        if 'VersionId' in obj:
            resp_content["versionID"] = obj['VersionId']

        resp_str = json.dumps(resp_content)
        self.finish(resp_str)
