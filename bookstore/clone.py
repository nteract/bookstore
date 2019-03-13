import json

import aiobotocore

from notebook.base.handlers import APIHandler, path_regex
from notebook.utils import url_path_join
from tornado import web

from .s3_paths import s3_path, s3_display_path
from .bookstore_config import BookstoreSettings


class BookstoreCloneHandler(APIHandler):
    """Clone a notebook from s3."""

    def initialize(self):
        # create an easy helper to get at our bookstore settings quickly
        self.bookstore_settings = BookstoreSettings(config=self.config)

        self.session = aiobotocore.get_session()

    async def _clone(self, s3_bucket, file_key):
        path = file_key

        self.log.info(f"bucket: {s3_bucket}")
        self.log.info(f"key: {file_key}")
        full_s3_path = s3_path(s3_bucket, path)

        async with self.session.create_client(
            's3',
            aws_secret_access_key=self.bookstore_settings.s3_secret_access_key,
            aws_access_key_id=self.bookstore_settings.s3_access_key_id,
            endpoint_url=self.bookstore_settings.s3_endpoint_url,
            region_name=self.bookstore_settings.s3_region_name,
        ) as client:
            self.log.info("Processing published write of %s", path)
            obj = await client.get_object(Bucket=s3_bucket, Key=file_key)
            content = await obj['Body'].read()
            self.log.info("Done with published write of %s", path)

        self.set_status(201)
        resp_content = {"s3_path": full_s3_path}
        model = {"type": "notebook", "content": json.loads(content.decode('utf-8'))}

        if 'VersionId' in obj:
            resp_content["versionID"] = obj['VersionId']
        resp_str = json.dumps(resp_content)
        self.finish(resp_str)
        return model

    async def get(self):
        """Clone a notebook to a given path.
        
        The payload for this should match that of the contents API for POST.
        
        Also, you could … *not* do that while still prototyping.
        That's ok! 
        But this all should go away.
        """
        s3_bucket = self.get_argument("s3_bucket", "")
        file_key = self.get_argument("s3_key", "")
        self.log.info("About to clone from %s", file_key)

        if file_key == '' or file_key == '/':
            raise web.HTTPError(400, "Must have a key to clone from")
        model = await self._clone(s3_bucket, file_key)

        self.contents_manager.save(model, file_key)
