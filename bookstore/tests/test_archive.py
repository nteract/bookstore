"""Tests for archive"""
import pytest
from pytest import skip

from bookstore.archive import ArchiveRecord, BookstoreContentsArchiver


def test_create_contentsarchiver():
    assert BookstoreContentsArchiver()


def test_create_contentsarchiver_invalid_args_count():
    with pytest.raises(TypeError):
        BookstoreContentsArchiver(42, True, 'hello')


@pytest.mark.skip
async def test_archive_failure_on_no_lock():
    archiver = BookstoreContentsArchiver()
    assert archiver

    record = ArchiveRecord('workspace/project', 'my_notebook', 100.2)
    assert record

    await archiver.archive(record)
