import json

import aiobotocore

from botocore.exceptions import ClientError
from nbformat import ValidationError, validate as validate_nb
from notebook.base.handlers import APIHandler, path_regex
from notebook.services.contents.handlers import validate_model
from tornado import web

from .bookstore_config import BookstoreSettings
from .s3_paths import s3_path
from .s3_paths import s3_key
from .s3_paths import s3_display_path
from .utils import url_path_join


class BookstorePublishAPIHandler(APIHandler):
    """Publish a notebook to the publish path"""

    def initialize(self):
        """Initialize a helper to get bookstore settings and session information quickly"""
        self.bookstore_settings = BookstoreSettings(config=self.config)
        self.session = aiobotocore.get_session()

    @web.authenticated
    async def put(self, path):
        """Publish a notebook on a given path.

        PUT /api/bookstore/publish

        The payload directly matches the contents API for PUT.
        """
        self.log.info("Attempt publishing to %s", path)

        if path == '' or path == '/':
            raise web.HTTPError(400, "Must provide a path for publishing")

        model = self.get_json_body()
        self.validate_model(model)
        resp = await self._publish(model['content'], path.lstrip('/'))
        self.set_status(201)
        self.finish(resp)

    def validate_model(self, model):
        """Checks that the model given to the API handler meets bookstore's expected structure for a notebook.

        Pattern for surfacing nbformat validation errors originally written in
        https://github.com/jupyter/notebook/blob/a44a367c219b60a19bee003877d32c3ff1ce2412/notebook/services/contents/manager.py#L353-L355

        Raises
        ------
        tornado.web.HTTPError
            Your model does not validate correctly
        """
        if not model:
            raise web.HTTPError(400, "Bookstore cannot publish an empty model")
        if model.get('type', "") != 'notebook':
            raise web.HTTPError(400, "Bookstore only publishes notebooks")

        content = model.get('content', {})
        if content == {}:
            raise web.HTTPError(400, "Bookstore cannot publish empty contents")
        try:
            validate_nb(content)
        except ValidationError as e:
            raise web.HTTPError(
                400,
                "Bookstore cannot publish invalid notebook. "
                "Validation errors are as follows: "
                f"{e.message} {json.dumps(e.instance, indent=1, default=lambda obj: '<UNKNOWN>')}",
            )

    async def _publish(self, content, path):
        """Publish notebook model to the path"""
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
            try:
                obj = await client.put_object(
                    Bucket=self.bookstore_settings.s3_bucket,
                    Key=s3_object_key,
                    Body=json.dumps(content),
                )
            except ClientError as e:
                status_code = e.response['ResponseMetadata'].get('HTTPStatusCode')
                raise web.HTTPError(status_code, e.args[0])
            self.log.info("Done with published write of %s", path)

        resp_content = self.prepare_response(path, obj)
        resp_str = json.dumps(resp_content)
        return resp_str

    def prepare_response(self, path, obj):

        full_s3_path = s3_path(
            self.bookstore_settings.s3_bucket, self.bookstore_settings.published_prefix, path
        )

        resp_content = {"s3path": full_s3_path}

        if 'VersionId' in obj:
            resp_content["versionID"] = obj['VersionId']

        return resp_content
