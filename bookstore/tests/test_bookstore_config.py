"""Tests for bookstore config"""
import pytest

from bookstore.bookstore_config import BookstoreSettings, validate_bookstore


def test_validate_bookstore_defaults():
    settings = BookstoreSettings()
    assert validate_bookstore(settings)

def test_validate_bookstore_endpoint():
    settings2 = BookstoreSettings(s3_endpoint_url="")
    assert not validate_bookstore(settings2)
