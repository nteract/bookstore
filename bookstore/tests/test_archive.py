"""Tests for archive"""
import asyncio
import pytest

from bookstore.archive import ArchiveRecord, BookstoreContentsArchiver
from nbformat.v4 import new_notebook


def test_create_contentsarchiver():
    assert BookstoreContentsArchiver()


def test_create_contentsarchiver_invalid_args_count():
    with pytest.raises(TypeError):
        BookstoreContentsArchiver(42, True, 'hello')


@pytest.mark.asyncio
async def test_archive_failure_on_no_lock():
    archiver = BookstoreContentsArchiver()
    assert archiver

    record = ArchiveRecord('workspace/project', 'my_notebook', 100.2)
    assert record

    await archiver.archive(record)


def test_pre_save_hook():
    archiver = BookstoreContentsArchiver()
    model = {"type": "notebook", "content": new_notebook()}
    target_path = "my_notebook_path.ipynb"

    archiver.run_pre_save_hook(model, target_path)
