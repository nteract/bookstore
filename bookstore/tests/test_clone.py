from unittest.mock import Mock

import pytest
from tornado.testing import AsyncTestCase, gen_test
from tornado.web import Application, HTTPError
from tornado.httpserver import HTTPRequest

from jinja2 import Environment

from ..clone import BookstoreCloneHandler

def handler(uri='/api/bookstore/cloned'):
    mock_application = Mock(spec=Application, ui_methods={}, ui_modules={}, settings={})
    payload_request = HTTPRequest(method='GET', uri=uri, headers=None, body=None, connection=Mock())

    handler = BookstoreCloneHandler(mock_application, payload_request)
    return handler


class TestCloneHandler(AsyncTestCase):
    def setUp(self):
        super().setUp()
        self.mock_application = Mock(
            spec=Application, ui_methods={}, ui_modules={}, settings={'jinja2_env': Environment()}
        )

    def get_handler(self, uri):
        payload_request = HTTPRequest(
            method='GET', uri=uri, headers=None, body=None, connection=Mock()
        )
        return BookstoreCloneHandler(self.mock_application, payload_request)

    @gen_test
    async def test_get_no_param(self):
        empty_handler = self.get_handler('/api/bookstore/cloned')
        with pytest.raises(HTTPError):
            await empty_handler.get()

    @gen_test
    async def test_get_no_bucket(self):
        no_bucket_handler = self.get_handler('/api/bookstore/cloned?s3_bucket=&s3_key=hi')
        with pytest.raises(HTTPError):
            await no_bucket_handler.get()

    @gen_test
    async def test_get_no_object_key(self):
        no_object_key_handler = self.get_handler('/api/bookstore/cloned?s3_bucket=hello&s3_key=')
        with pytest.raises(HTTPError):
            await no_object_key_handler.get()

    @gen_test
    async def test_get_success(self):
        success_handler = self.get_handler('/api/bookstore/cloned?s3_bucket=hello&s3_key=my_key')
        await success_handler.get()
