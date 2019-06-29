import asyncio
import json

from unittest.mock import Mock

import pytest

from bookstore.publish import BookstorePublishAPIHandler
from nbformat.v4 import new_notebook
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
                "s3_bucket": "my_bucket",
                "published_prefix": "custom_prefix",
            }
        }
        config = Config(mock_settings)

        self.mock_application = Mock(
            spec=Application, ui_methods={}, ui_modules={}, settings={"config": config}
        )

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
        no_path_handler = self.put_handler('/bookstore/publish/')
        with pytest.raises(HTTPError):
            await no_path_handler.put('')

    @gen_test
    async def test_put_no_body(self):
        no_body_handler = self.put_handler('/bookstore/publish/hi')
        with pytest.raises(HTTPError):
            await no_body_handler.put('hi')

    @gen_test
    async def test_put_s3_error(self):
        """this test includes a valid body so that we get to the s3 part of our system"""
        body_dict = {'content': new_notebook(), 'type': "notebook"}
        ok_body_handler = self.put_handler('/bookstore/publish/hi', body_dict=body_dict)
        with pytest.raises(HTTPError):
            await ok_body_handler.put('hi')

    def test_prepare_response(self):
        expected = {"s3_path": "s3://my_bucket/custom_prefix/mylocal/path", "versionID": "eeeeAB"}
        empty_handler = self.put_handler('/bookstore/publish/hi')
        actual = empty_handler.prepare_response(
            {"VersionId": "eeeeAB"}, "s3://my_bucket/custom_prefix/mylocal/path"
        )
        assert actual == expected

    def test_validate_model_no_type(self):
        body_dict = {'content': {}}
        empty_handler = self.put_handler('/bookstore/publish/hi')
        with pytest.raises(HTTPError):
            empty_handler.validate_model(body_dict)

    def test_validate_model_wrong_type(self):
        body_dict = {'content': {}, 'type': "file"}
        empty_handler = self.put_handler('/bookstore/publish/hi')
        with pytest.raises(HTTPError):
            empty_handler.validate_model(body_dict)

    def test_validate_model_empty_content(self):
        body_dict = {'content': {}, 'type': "notebook"}
        empty_handler = self.put_handler('/bookstore/publish/hi')
        with pytest.raises(HTTPError):
            empty_handler.validate_model(body_dict)

    def test_validate_model_bad_notebook(self):
        bad_notebook = new_notebook()
        bad_notebook['other_field'] = "hello"
        body_dict = {'content': bad_notebook, 'type': "notebook"}
        empty_handler = self.put_handler('/bookstore/publish/hi')
        with pytest.raises(HTTPError):
            empty_handler.validate_model(body_dict)

    def test_validate_model_good_notebook(self):
        body_dict = {'content': new_notebook(), 'type': "notebook"}
        empty_handler = self.put_handler('/bookstore/publish/hi')
        empty_handler.validate_model(body_dict)
