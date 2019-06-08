"""Tests for s3 paths"""
import pytest

from bookstore.s3_paths import s3_display_path, s3_key


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


def test_s3_key_no_prefix():
    with pytest.raises(TypeError):
        s3_key(path='s3://mybucket')


def test_s3_key_invalid_prefix():
    prefix = 1234
    with pytest.raises(AttributeError):
        s3_key(prefix)


def test_s3_key_valid_parameters():
    prefix = 'workspace'
    path = 'project/manufacturing'
    assert s3_key(prefix, path) == 'workspace/project/manufacturing'
