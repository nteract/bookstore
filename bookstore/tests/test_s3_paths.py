"""Tests for s3 paths"""
import pytest

from bookstore.s3_paths import s3_display_path


def test_s3_paths():
    bucket = 'mybucket'
    prefix = 'yo'
    path = 'pickles'
    assert s3_display_path(bucket, prefix, path) == 's3://mybucket/yo/pickles'


def test_s3_paths_no_path():
    bucket = 'mybucket'
    prefix = 'yo'
    assert s3_display_path(bucket, prefix) == 's3://mybucket/yo'


def test_s3_paths_no_prefix():
    bucket = 'mybucket'
    path = 'pickles'
    with pytest.raises(NameError):
        s3_display_path(bucket, prefix, path)


def test_join():
    pass
