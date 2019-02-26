import json

import aiobotocore

from notebook.base.handlers import APIHandler, path_regex
from notebook.utils import url_path_join
from tornado import web

from .s3_paths import s3_path, s3_key, s3_display_path
from .bookstore_config import BookstoreSettings


class BookstoreCloneHandler(APIHandler):
    """Clone a notebook from s3."""

    def initialize(self):
        # create an easy helper to get at our bookstore settings quickly
        self.bookstore_settings = BookstoreSettings(config=self.config)

        self.session = aiobotocore.get_session()

    async def _clone(self, path):
        full_s3_path = s3_path(
            self.bookstore_settings.s3_bucket, path
        )
        file_key = path

        async with self.session.create_client(
            's3',
            aws_secret_access_key=self.bookstore_settings.s3_secret_access_key,
            aws_access_key_id=self.bookstore_settings.s3_access_key_id,
            endpoint_url=self.bookstore_settings.s3_endpoint_url,
            region_name=self.bookstore_settings.s3_region_name,
        ) as client:
            self.log.info("Processing published write of %s", path)
            obj = await client.get_object(
                Bucket=self.bookstore_settings.s3_bucket, Key=file_key
            )
            content = await obj['Body'].read()
            self.log.info("Done with published write of %s", path)
        
        self.set_status(201)
        resp_content = {
            "s3path": full_s3_path,
            "content": content.decode('utf-8')
        }
        
        self.log.info(obj)
        if 'VersionId' in obj:
            resp_content["versionID"] = obj['VersionId']
        
        resp_str = json.dumps(resp_content)
        self.finish(resp_str)

    async def get(self, path=''):
        """Clone a notebook to a given path.
        
        The payload for this should match that of the contents API for POST.
        
        Also, you could … *not* do that while still prototyping.
        That's ok! 
        But this all should go away.
        """
        self.log.info("About to clone to %s", path)

        if path == '' or path == '/':
            raise web.HTTPError(400, "Must have a path to publish to")
        await self._clone(path.lstrip('/'))

        

