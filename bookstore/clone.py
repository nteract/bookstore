"""Handler to clone notebook from storage."""
import json
import os

import aiobotocore
from jinja2 import FileSystemLoader
from notebook.base.handlers import IPythonHandler
from tornado import web

from . import PACKAGE_DIR
from .bookstore_config import BookstoreSettings
from .s3_paths import s3_path
from .utils import url_path_join

BOOKSTORE_FILE_LOADER = FileSystemLoader(PACKAGE_DIR)


class BookstoreCloneHandler(IPythonHandler):
    """Handle notebook clone from storage.

    Provides API handling for ``GET`` and ``POST`` when cloning a notebook
    from storage (S3). Launches a user interface cloning options page when
    ``GET`` is sent.

    Methods
    -------
    initialize(self)
        Helper to access bookstore settings.
    get(self)
        Checks for valid storage settings and render a UI for clone options.
    construct_template_params(self, s3_bucket, s3_object_key)
        Helper to populate Jinja template for cloning option page.
    post(self)
        Clone a notebook from the location specified by the payload.
    get_template(self, name)
        Loads a Jinja template and its related settings.

    See also
    --------
    `Jupyter Notebook reference on Custom Handlers <https://jupyter-notebook.readthedocs.io/en/stable/extending/handlers.html#registering-custom-handlers>`_
    """

    def initialize(self):
        """Helper to retrieve bookstore setting for the session."""
        self.bookstore_settings = BookstoreSettings(config=self.config)

        self.session = aiobotocore.get_session()

    async def _clone(self, s3_bucket, s3_key_file):

        self.log.info(f"bucket: {s3_bucket}")
        self.log.info(f"key: {s3_key_file}")
        full_s3_path = s3_path(s3_bucket, s3_key_file)

        # TODO bookstore settings review https://github.com/nteract/bookstore/pull/75/files?file-filters%5B%5D=.py#r281830978
        async with self.session.create_client(
            's3',
            aws_secret_access_key=self.bookstore_settings.s3_secret_access_key,
            aws_access_key_id=self.bookstore_settings.s3_access_key_id,
            endpoint_url=self.bookstore_settings.s3_endpoint_url,
            region_name=self.bookstore_settings.s3_region_name,
        ) as client:
            self.log.info("Processing published write of %s", s3_key_file)
            obj = await client.get_object(Bucket=s3_bucket, Key=s3_key_file)
            content = await obj['Body'].read()
            self.log.info("Done with published write of %s", s3_key_file)

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
        """GET /api/bookstore/cloned

        Renders an options page that will allow you to clone a notebook
        from a specific bucket.
        """
        s3_bucket = self.get_argument("s3_bucket")
        if s3_bucket == '' or s3_bucket == "/":
            raise web.HTTPError(400, "Must have a bucket to clone from")

        # s3_paths module has an s3_key function; s3_object_key avoids confusion
        s3_object_key = self.get_argument("s3_key")
        if s3_object_key == '' or s3_object_key == '/':
            raise web.HTTPError(400, "Must have a key to clone from")

        self.log.info("Setting up cloning landing page from %s", s3_object_key)

        template_params = self.construct_template_params(s3_bucket, s3_object_key)
        self.set_header('Content-Type', 'text/html')
        self.write(self.render_template('clone.html', **template_params))

    def construct_template_params(self, s3_bucket, s3_object_key):
        """Helper that takes valid S3 parameters and populates UI template"""
        base_uri = f"{self.request.protocol}://{self.request.host}"
        clone_api_url = url_path_join(base_uri, self.base_url, "/api/bookstore/cloned")
        redirect_contents_url = url_path_join(base_uri, self.default_url)
        template_params = {
            "s3_bucket": s3_bucket,
            "s3_key": s3_object_key,
            "clone_api_url": clone_api_url,
            "redirect_contents_url": redirect_contents_url,
        }
        return template_params

    @web.authenticated
    async def post(self):
        """POST /api/bookstore/cloned

        Clone a notebook to the path specified in the payload.

        The payload type for the request should be::

            {
            "s3_bucket": string,
            "s3_key": string,
            "target_path"?: string
            }

        The response payload should match the standard Jupyter contents
        API POST response.
        """
        model = self.get_json_body()
        # TODO Fail fast here if no s3 key
        s3_bucket = model.get("s3_bucket", "")
        # s3_paths module has an s3_key function; file_key avoids confusion
        s3_key_file = model.get("s3_key", "")
        target_path = model.get("target_path", "") or os.path.basename(
            os.path.relpath(s3_key_file)
        )

        self.log.info("About to clone from %s", s3_key_file)

        if s3_key_file == '' or s3_key_file == '/':
            raise web.HTTPError(400, "Must have an S3 key to perform clone.")
        model = await self._clone(s3_bucket, s3_key_file)
        self.set_header('Content-Type', 'application/json')
        path = self.contents_manager.increment_filename(target_path)
        model['name'] = os.path.basename(os.path.relpath(path))
        model['path'] = os.path.relpath(path)
        self.contents_manager.save(model, path)
        self.finish(model)

    def get_template(self, name):
        """Loads a Jinja template by name."""
        return BOOKSTORE_FILE_LOADER.load(self.settings['jinja2_env'], name)
