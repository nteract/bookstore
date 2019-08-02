"""Tests for bookstore config"""
import logging

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
    """Tests that cloning from s3_bucket can be disabled."""
    expected = {
        "bookstore_valid": True,
        "publish_valid": True,
        "archive_valid": True,
        "s3_clone_valid": False,
        "fs_clone_valid": False,
    }
    settings = BookstoreSettings(s3_bucket="A_bucket", enable_s3_cloning=False)
    assert validate_bookstore(settings) == expected


def test_enable_fs_cloning():
    """Tests that file system cloning works even if s3 cloning is disabled."""
    expected = {
        "bookstore_valid": False,
        "publish_valid": False,
        "archive_valid": False,
        "s3_clone_valid": False,
        "fs_clone_valid": True,
    }
    settings = BookstoreSettings(enable_s3_cloning=False, fs_cloning_basedir="/Users/bookstore")
    assert validate_bookstore(settings) == expected


def test_relative_basepath(caplog):
    """Tests that file system cloning works even if s3 cloning is disabled."""
    expected = {
        "bookstore_valid": False,
        "publish_valid": False,
        "archive_valid": False,
        "s3_clone_valid": False,
        "fs_clone_valid": False,
    }
    fs_cloning_basedir = "Users/jupyter"
    settings = BookstoreSettings(enable_s3_cloning=False, fs_cloning_basedir=fs_cloning_basedir)
    with caplog.at_level(logging.INFO):
        actual = validate_bookstore(settings)
    assert actual == expected
    assert f"{fs_cloning_basedir} is not an absolute path," in caplog.text
