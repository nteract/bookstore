"""Tests for handlers"""
from unittest.mock import Mock

import pytest
import logging
from unittest.mock import Mock

from bookstore._version import __version__
from bookstore.handlers import collect_handlers, build_settings_dict, BookstoreVersionHandler
from bookstore.bookstore_config import BookstoreSettings, validate_bookstore
from bookstore.clone import BookstoreCloneHandler, BookstoreCloneAPIHandler
from bookstore.publish import BookstorePublishAPIHandler
from notebook.base.handlers import path_regex
from tornado.testing import AsyncTestCase
from tornado.web import Application, HTTPError
from tornado.httpserver import HTTPRequest
from traitlets.config import Config

log = logging.getLogger('test_handlers')
version = __version__

from traitlets.config import Config


def test_collect_handlers_all():
    expected = [
        ('/api/bookstore', BookstoreVersionHandler),
        ('/api/bookstore/publish%s' % path_regex, BookstorePublishAPIHandler),
        ('/api/bookstore/clone(?:/?)*', BookstoreCloneAPIHandler),
        ('/bookstore/clone(?:/?)*', BookstoreCloneHandler),
    ]
    web_app = Application()
    mock_settings = {"BookstoreSettings": {"s3_bucket": "mock_bucket"}}
    bookstore_settings = BookstoreSettings(config=Config(mock_settings))
    validation = validate_bookstore(bookstore_settings)
    handlers = collect_handlers(log, '/', validation)
    assert expected == handlers


def test_collect_handlers_no_clone():
    expected = [
        ('/api/bookstore', BookstoreVersionHandler),
        ('/api/bookstore/publish%s' % path_regex, BookstorePublishAPIHandler),
    ]
    web_app = Application()
    mock_settings = {"BookstoreSettings": {"s3_bucket": "mock_bucket", "enable_cloning": False}}
    bookstore_settings = BookstoreSettings(config=Config(mock_settings))
    validation = validate_bookstore(bookstore_settings)
    handlers = collect_handlers(log, '/', validation)
    assert expected == handlers


def test_collect_handlers_no_publish():
    expected = [
        ('/api/bookstore', BookstoreVersionHandler),
        ('/api/bookstore/clone(?:/?)*', BookstoreCloneAPIHandler),
        ('/bookstore/clone(?:/?)*', BookstoreCloneHandler),
    ]
    web_app = Application()
    mock_settings = {"BookstoreSettings": {"s3_bucket": "mock_bucket", "published_prefix": ""}}
    bookstore_settings = BookstoreSettings(config=Config(mock_settings))
    validation = validate_bookstore(bookstore_settings)
    handlers = collect_handlers(log, '/', validation)
    assert expected == handlers


def test_collect_handlers_only_version():
    expected = [('/api/bookstore', BookstoreVersionHandler)]
    web_app = Application()
    mock_settings = {"BookstoreSettings": {"enable_cloning": False}}
    bookstore_settings = BookstoreSettings(config=Config(mock_settings))
    validation = validate_bookstore(bookstore_settings)
    handlers = collect_handlers(log, '/', validation)
    assert expected == handlers


@pytest.fixture(scope="class")
def bookstore_settings(request):
    mock_settings = {
        "BookstoreSettings": {
            "s3_access_key_id": "mock_id",
            "s3_secret_access_key": "mock_access",
            "s3_bucket": "my_bucket",
        }
    }
    config = Config(mock_settings)
    bookstore_settings = BookstoreSettings(config=config)
    if request.cls is not None:
        request.cls.bookstore_settings = bookstore_settings
    return bookstore_settings


def test_build_settings_dict(bookstore_settings):
    expected = {
        'features': {
            'archive_valid': True,
            'bookstore_valid': True,
            'publish_valid': True,
            'clone_valid': True,
        },
        'release': version,
    }
    validation = validate_bookstore(bookstore_settings)
    assert expected == build_settings_dict(validation)


@pytest.mark.usefixtures("bookstore_settings")
class TestCloneAPIHandler(AsyncTestCase):
    def setUp(self):
        super().setUp()

        validation = validate_bookstore(self.bookstore_settings)
        self.mock_application = Mock(
            spec=Application,
            ui_methods={},
            ui_modules={},
            settings={"bookstore": build_settings_dict(validation)},
            transforms=[],
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
        return BookstoreVersionHandler(app, payload_request)

    def test_get(self):
        """This is a simple test of the get API at /api/bookstore

        The most notable feature is the need to set _transforms on the handler.

        The default value of handler()._transforms is `None`.
        This is iterated over when handler().flush() is called, raising a TypeError.
        
        In normal usage, the application assigns this when it creates a handler delegate.

        Because our mock application does not do this 
        As a result this raises an error when self.finish() (and therefore self.flush()) is called.

        At runtime on a live Jupyter server, application.transforms == [].
        """
        get_handler = self.get_handler('/api/bookstore/')
        setattr(get_handler, '_transforms', [])
        return_val = get_handler.get()
        assert return_val is None

    def test_build_response(self):
        empty_handler = self.get_handler('/api/bookstore/')
        expected = {
            'features': {
                'archive_valid': True,
                'bookstore_valid': True,
                'publish_valid': True,
                'clone_valid': True,
            },
            'release': version,
        }
        assert empty_handler.build_response_dict() == expected
