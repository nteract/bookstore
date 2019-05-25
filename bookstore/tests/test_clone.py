from unittest.mock import Mock

import pytest
from tornado.testing import AsyncTestCase, gen_test
from tornado.web import Application, HTTPError
from tornado.httpserver import HTTPRequest

from ..clone import BookstoreCloneHandler

def handler(uri='/api/bookstore/cloned'):
    mock_application = Mock(spec=Application, ui_methods={}, ui_modules={}, settings={})
    payload_request = HTTPRequest(method='GET', uri=uri, headers=None, body=None, connection=Mock())

    handler = BookstoreCloneHandler(mock_application, payload_request)
    return handler


class TestSomeHandler(AsyncTestCase):
    @gen_test
    def test_no_param(self):
        with pytest.raises(HTTPError):
            yield handler().get()
