"""Tests for bookstore config"""
import pytest

from bookstore.bookstore_config import BookstoreSettings, validate_bookstore


def test_validate_bookstore_defaults():
    """Tests that all bookstore validates with default values."""
    settings = BookstoreSettings()
    assert not validate_bookstore(settings)


def test_validate_bookstore_published():
    """Tests that bookstore does not validate with an empty published_prefix."""
    settings = BookstoreSettings(published_prefix="")
    assert not validate_bookstore(settings)


def test_validate_bookstore_workspace():
    """Tests that bookstore does not validate with an empty workspace_prefix."""
    settings = BookstoreSettings(workspace_prefix="")
    assert not validate_bookstore(settings)


def test_validate_bookstore_endpoint():
    """Tests that bookstore does not validate with an empty s3_endpoint_url."""
    settings = BookstoreSettings(s3_endpoint_url="")
    assert not validate_bookstore(settings)


def test_validate_bookstore_bucket():
    """Tests that bookstore does not validate with an empty s3_bucket."""
    settings = BookstoreSettings(s3_bucket="A_bucket")
    assert validate_bookstore(settings)
