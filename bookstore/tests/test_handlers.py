"""Tests for handlers"""
import pytest
import logging

from unittest.mock import Mock

from bookstore.handlers import build_handlers, BookstoreVersionHandler
from bookstore.bookstore_config import BookstoreSettings, validate_bookstore
from bookstore.clone import BookstoreCloneHandler, BookstoreCloneAPIHandler
from bookstore.publish import BookstorePublishHandler

from notebook.base.handlers import path_regex
from tornado.web import Application
from traitlets.config import Config

log = logging.getLogger('test_handlers')


def test_handlers():
    pass


def test_build_handlers_all():
    web_app = Application()
    mock_settings = {"BookstoreSettings": {"s3_bucket": "mock_bucket"}}
    bookstore_settings = BookstoreSettings(config=Config(mock_settings))
    validation = validate_bookstore(bookstore_settings)
    handlers = build_handlers(log, '/', validation)
    expected = [
        ('/api/bookstore', BookstoreVersionHandler),
        ('/api/bookstore/publish%s' % path_regex, BookstorePublishHandler),
        ('/api/bookstore/clone(?:/?)*', BookstoreCloneAPIHandler),
        ('/bookstore/clone(?:/?)*', BookstoreCloneHandler),
    ]

    assert expected == handlers


def test_build_handlers_no_clone():
    web_app = Application()
    mock_settings = {"BookstoreSettings": {"s3_bucket": "mock_bucket", "enable_cloning": False}}
    bookstore_settings = BookstoreSettings(config=Config(mock_settings))
    validation = validate_bookstore(bookstore_settings)
    handlers = build_handlers(log, '/', validation)
    expected = [
        ('/api/bookstore', BookstoreVersionHandler),
        ('/api/bookstore/publish%s' % path_regex, BookstorePublishHandler),
    ]

    assert expected == handlers


def test_build_handlers_no_publish():
    web_app = Application()
    mock_settings = {"BookstoreSettings": {"s3_bucket": "mock_bucket", "published_prefix": ""}}
    bookstore_settings = BookstoreSettings(config=Config(mock_settings))
    validation = validate_bookstore(bookstore_settings)
    handlers = build_handlers(log, '/', validation)
    expected = [
        ('/api/bookstore', BookstoreVersionHandler),
        ('/api/bookstore/clone(?:/?)*', BookstoreCloneAPIHandler),
        ('/bookstore/clone(?:/?)*', BookstoreCloneHandler),
    ]

    assert expected == handlers


def test_build_handlers_only_version():
    web_app = Application()
    mock_settings = {"BookstoreSettings": {"enable_cloning": False}}
    bookstore_settings = BookstoreSettings(config=Config(mock_settings))
    validation = validate_bookstore(bookstore_settings)
    handlers = build_handlers(log, '/', validation)
    expected = [('/api/bookstore', BookstoreVersionHandler)]

    assert expected == handlers
