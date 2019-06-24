import asyncio
import json

from unittest.mock import Mock

import pytest

from bookstore.publish import BookstorePublishAPIHandler
from tornado.testing import AsyncTestCase, gen_test
from tornado.web import Application, HTTPError
from tornado.httpserver import HTTPRequest
from traitlets.config import Config


def test_create_publish_handler_no_params():
    with pytest.raises(TypeError):
        assert BookstorePublishAPIHandler()


class TestPublishAPIHandler(AsyncTestCase):
    def setUp(self):
        super().setUp()
        mock_settings = {
            "BookstoreSettings": {
                "s3_access_key_id": "mock_id",
                "s3_secret_access_key": "mock_access",
            }
        }
        config = Config(mock_settings)

        self.mock_application = Mock(spec=Application, ui_methods={}, ui_modules={}, settings={})

    def put_handler(self, uri, body_dict=None, app=None):
        if body_dict is None:
            body_dict = {}
        if app is None:
            app = self.mock_application
        connection = Mock(context=Mock(protocol="https"))
        body = json.dumps(body_dict).encode('utf-8')
        payload_request = HTTPRequest(
            method='PUT',
            uri=uri,
            headers={"Host": "localhost:8888"},
            body=body,
            connection=connection,
        )
        return BookstorePublishAPIHandler(app, payload_request)

    @gen_test
    async def test_put_no_path(self):
        empty_handler = self.put_handler('/bookstore/publish/')
        with pytest.raises(HTTPError):
            await empty_handler.put('')

    @gen_test
    async def test_put_no_body(self):
        empty_handler = self.put_handler('/bookstore/publish/hi')
        with pytest.raises(HTTPError):
            await empty_handler.put('hi')

    @gen_test
    async def test_put_bad_body(self):
        body_dict = {'content': 2}
        empty_handler = self.put_handler('/bookstore/publish/hi', body_dict=body_dict)
        with pytest.raises(HTTPError):
            await empty_handler.put('hi')

