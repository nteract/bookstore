import json

import aiobotocore

from notebook.base.handlers import APIHandler, path_regex
from notebook.utils import url_path_join
from tornado import web

from ._version import __version__, version_info
from .bookstore_config import BookstoreSettings
from .s3_paths import s3_path, s3_key, s3_display_path


version = __version__


class BookstoreVersionHandler(APIHandler):
    """Returns the version of bookstore currently running. Used mostly to lay foundations
    for this package though frontends can use this endpoint for feature detection.
    """

    @web.authenticated
    def get(self):
        self.finish(json.dumps({"bookstore": True, "version": version}))


# NOTE: We need to ensure that publishing is not configured if bookstore settings are not
# set. Because of how the APIHandlers cannot be configurable, all we can do is reach into settings
# For applications this will mean checking the config and then applying it in


class BookstorePublishHandler(APIHandler):
    """Publish a notebook to the publish path"""

    def __init__(self, *args, **kwargs):
        super(APIHandler, self).__init__(*args, **kwargs)
        # create an easy helper to get at our bookstore settings quickly
        self.bookstore_settings = BookstoreSettings(config=self.config)

        self.session = aiobotocore.get_session()

    async def _publish(self, model, path):
        if model['type'] != 'notebook':
            raise web.HTTPError(400, "bookstore only publishes notebooks")
        content = model['content']

        full_s3_path = s3_path(
            self.bookstore_settings.s3_bucket, self.bookstore_settings.published_prefix, path
        )
        file_key = s3_key(self.bookstore_settings.published_prefix, path)

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
                Bucket=self.bookstore_settings.s3_bucket, Key=file_key, Body=json.dumps(content)
            )
            self.log.info("Done with published write of %s", path)

        self.set_status(201)

        resp_content = {"s3path": full_s3_path}

        if 'VersionId' in obj:
            resp_content["versionID"] = obj['VersionId']

        resp_str = json.dumps(resp_content)
        self.finish(resp_str)

    @web.authenticated
    async def put(self, path=''):
        """Publish a notebook on a given path. The payload for this directly matches that of the contents API for PUT.
        """
        self.log.info("About to publish %s", path)

        if path == '' or path == '/':
            raise web.HTTPError(400, "Must have a path to publish to")

        model = self.get_json_body()

        if model:
            await self._publish(model, path.lstrip('/'))
        else:
            raise web.HTTPError(400, "Cannot publish empty model")


def load_jupyter_server_extension(nb_app):
    web_app = nb_app.web_app
    host_pattern = '.*$'
    base_bookstore_pattern = url_path_join(web_app.settings['base_url'], '/api/bookstore')

    # Always enable the version handler
    web_app.add_handlers(host_pattern, [(base_bookstore_pattern, BookstoreVersionHandler)])

    if not nb_app.config.get("BookstoreSettings"):
        nb_app.log.info("Not enabling bookstore publishing since bookstore endpoint not configured")
    else:
        web_app.add_handlers(
            host_pattern,
            [
                (
                    url_path_join(base_bookstore_pattern, r"/published%s" % path_regex),
                    BookstorePublishHandler,
                )
            ],
        )
