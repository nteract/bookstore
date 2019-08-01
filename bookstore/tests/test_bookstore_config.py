"""Tests for bookstore config"""
import pytest

from bookstore.bookstore_config import BookstoreSettings, validate_bookstore


def test_validate_bookstore_defaults():
    """Tests that all bookstore validates with default values."""
    expected = {
        "bookstore_valid": False,
        "publish_valid": False,
        "archive_valid": False,
        "s3_clone_valid": True,
        "fs_clone_valid": False,
    }
    settings = BookstoreSettings()
    assert validate_bookstore(settings) == expected


def test_validate_bookstore_published():
    """Tests that bookstore does not validate with an empty published_prefix."""
    expected = {
        "bookstore_valid": True,
        "publish_valid": False,
        "archive_valid": True,
        "s3_clone_valid": True,
        "fs_clone_valid": False,
    }
    settings = BookstoreSettings(s3_bucket="A_bucket", published_prefix="")
    assert validate_bookstore(settings) == expected


def test_validate_bookstore_workspace():
    """Tests that bookstore does not validate with an empty workspace_prefix."""
    expected = {
        "bookstore_valid": True,
        "publish_valid": True,
        "archive_valid": False,
        "s3_clone_valid": True,
        "fs_clone_valid": False,
    }
    settings = BookstoreSettings(s3_bucket="A_bucket", workspace_prefix="")
    assert validate_bookstore(settings) == expected


def test_validate_bookstore_endpoint():
    """Tests that bookstore does not validate with an empty s3_endpoint_url."""
    expected = {
        "bookstore_valid": False,
        "publish_valid": False,
        "archive_valid": False,
        "s3_clone_valid": True,
        "fs_clone_valid": False,
    }
    settings = BookstoreSettings(s3_endpoint_url="")
    assert validate_bookstore(settings) == expected


def test_validate_bookstore_bucket():
    """Tests that bookstore features validate with an s3_bucket."""
    expected = {
        "bookstore_valid": True,
        "publish_valid": True,
        "archive_valid": True,
        "s3_clone_valid": True,
        "fs_clone_valid": False,
    }
    settings = BookstoreSettings(s3_bucket="A_bucket")
    assert validate_bookstore(settings) == expected


def test_disable_cloning():
    """Tests that cloning can be disabled when s3_bucket is provided."""
    expected = {
        "bookstore_valid": True,
        "publish_valid": True,
        "archive_valid": True,
        "s3_clone_valid": False,
        "fs_clone_valid": False
    }
    settings = BookstoreSettings(s3_bucket="A_bucket", enable_cloning=False)
    assert validate_bookstore(settings) == expected
