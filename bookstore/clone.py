import json
import os

import aiobotocore

from notebook.base.handlers import IPythonHandler
from tornado import web
from jinja2 import FileSystemLoader

from . import PACKAGE_DIR
from .s3_paths import s3_path
from .bookstore_config import BookstoreSettings


BOOKSTORE_FILE_LOADER = FileSystemLoader(PACKAGE_DIR)


class BookstoreCloneHandler(IPythonHandler):
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

        resp_content = {"s3_path": full_s3_path}
        model = {
            "type": "file",
            "format": "text",
            "mimetype": "text/plain",
            "content": content.decode('utf-8'),
        }
        self.set_status(201)

        if 'VersionId' in obj:
            resp_content["versionID"] = obj['VersionId']
        return model

    @web.authenticated
    async def get(self):
        """Open a page that will allow you to clone a notebook from a specific bucket.
        """
        s3_bucket = self.get_argument("s3_bucket", "")
        # s3_paths module has an s3_key function; file_key avoids confusion
        file_key = self.get_argument("s3_key", "")
        self.log.info("About to clone from %s", file_key)

        if file_key == '' or file_key == '/':
            raise web.HTTPError(400, "Must have a key to clone from")
        self.set_header('Content-Type', 'text/html')
        template_params = {"s3_bucket": s3_bucket, "s3_key": file_key}
        self.write(self.render_template('clone.html', **template_params))

    @web.authenticated
    async def post(self):
        """Clone a notebook to a given path.
        
        The payload for this should match that of the contents API for POST.
        
        Also, you could … *not* do that while still prototyping.
        That's ok! 
        But this all should go away.
        """
        model = self.get_json_body()
        s3_bucket = model.get("s3_bucket", "")
        # s3_paths module has an s3_key function; file_key avoids confusion
        file_key = model.get("s3_key", "")
        target_path = model.get("target_path", "") or os.path.basename(os.path.relpath(file_key))

        self.log.info("About to clone from %s", file_key)

        if file_key == '' or file_key == '/':
            raise web.HTTPError(400, "Must have a key to clone from")
        model = await self._clone(s3_bucket, file_key)
        self.set_header('Content-Type', 'text/html')
        path = self.contents_manager.increment_filename(target_path)
        model['name'] = os.path.basename(os.path.relpath(path))
        model['path'] = os.path.relpath(path)
        self.contents_manager.save(model, path)
        self.finish(model)

    def get_template(self, name):
        return BOOKSTORE_FILE_LOADER.load(self.settings['jinja2_env'], name)
