from unittest.mock import Mock

import pytest
from tornado.testing import AsyncTestCase, gen_test
from tornado.web import Application, HTTPError
from tornado.httpserver import HTTPRequest

from jinja2 import Environment

from ..clone import BookstoreCloneHandler


class TestCloneHandler(AsyncTestCase):
    def setUp(self):
        super().setUp()
        self.mock_application = Mock(
            spec=Application, ui_methods={}, ui_modules={}, settings={'jinja2_env': Environment()}
        )

    def get_handler(self, uri, app=None):
        if app is None:
            app = self.mock_application
        connection = Mock(context=Mock(protocol="https"))
        payload_request = HTTPRequest(
            method='GET',
            uri=uri,
            headers={"Host": "localhost:8888"},
            body=None,
            connection=connection,
        )
        return BookstoreCloneHandler(app, payload_request)

    @gen_test
    async def test_get_no_param(self):
        empty_handler = self.get_handler('/bookstore/clone')
        with pytest.raises(HTTPError):
            await empty_handler.get()

    @gen_test
    async def test_get_no_bucket(self):
        no_bucket_handler = self.get_handler('/bookstore/clone?s3_bucket=&s3_key=hi')
        with pytest.raises(HTTPError):
            await no_bucket_handler.get()

    @gen_test
    async def test_get_no_object_key(self):
        no_object_key_handler = self.get_handler('/bookstore/clone?s3_bucket=hello&s3_key=')
        with pytest.raises(HTTPError):
            await no_object_key_handler.get()

    @gen_test
    async def test_get_success(self):
        success_handler = self.get_handler('/bookstore/clone?s3_bucket=hello&s3_key=my_key')
        await success_handler.get()

    def test_gen_template_params(self):
        success_handler = self.get_handler('/bookstore/clone?s3_bucket=hello&s3_key=my_key')
        expected = {
            's3_bucket': 'hello',
            's3_key': 'my_key',
            'clone_api_url': 'https://localhost:8888/api/bookstore/clone',
            'redirect_contents_url': 'https://localhost:8888',
        }
        success_handler = self.get_handler('/bookstore/clone?s3_bucket=hello&s3_key=my_key')
        output = success_handler.construct_template_params(
            s3_bucket="hello", s3_object_key="my_key"
        )
        assert expected == output

    def test_gen_template_params_base_url(self):
        base_url_list = ['/my_base_url', '/my_base_url/', 'my_base_url/', 'my_base_url']
        expected = {
            's3_bucket': 'hello',
            's3_key': 'my_key',
            'clone_api_url': 'https://localhost:8888/my_base_url/api/bookstore/clone',
            'redirect_contents_url': 'https://localhost:8888',
        }
        for base_url in base_url_list:
            mock_app = Mock(
                spec=Application,
                ui_methods={},
                ui_modules={},
                settings={'jinja2_env': Environment(), "base_url": base_url},
            )

            success_handler = self.get_handler(
                '/bookstore/clone?s3_bucket=hello&s3_key=my_key', app=mock_app
            )
            output = success_handler.construct_template_params(
                s3_bucket="hello", s3_object_key="my_key"
            )
            assert expected == output
