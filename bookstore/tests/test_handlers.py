"""Tests for handlers"""
import pytest
import logging
from unittest.mock import Mock

from bookstore.handlers import collect_handlers, build_settings_dict, BookstoreVersionHandler
from bookstore.bookstore_config import BookstoreSettings, validate_bookstore
from bookstore.clone import BookstoreCloneHandler, BookstoreCloneAPIHandler
from bookstore.publish import BookstorePublishAPIHandler
from notebook.base.handlers import path_regex
from tornado.web import Application
from traitlets.config import Config

log = logging.getLogger('test_handlers')

from traitlets.config import Config

def test_handlers():
    pass


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
        "BookstoreSettings": {"s3_access_key_id": "mock_id", "s3_secret_access_key": "mock_access"}
    }
    config = Config(mock_settings)
    bookstore_settings = BookstoreSettings(config=config)
    if request.cls is not None:
        request.cls.bookstore_settings = bookstore_settings
    return bookstore_settings


def test_build_settings_dict(bookstore_settings):
    expected = {
        'validation': {'archive_valid': True, 'bookstore_valid': False, 'publish_valid': True},
        'version': '2.3.0.dev',
    }
    assert expected == build_settings_dict(bookstore_settings)
