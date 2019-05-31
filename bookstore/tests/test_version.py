"""Test version checking"""
import logging

import pytest

from .._version import _check_version


@pytest.mark.parametrize(
    'bookstore_version, msg',
    [
        ('', 'Bookstore has no version header'),
        ('1.0.0', 'deprecated bookstore'),
        ('2.0.0', 'Bookstore version is'),
        ('2.3.1', 'Bookstore version is'),
        ('xxxxx', 'Invalid version'),
    ],
)
def test_check_version(bookstore_version, msg, caplog):
    log = logging.getLogger()
    caplog.set_level(logging.DEBUG)
    _check_version(bookstore_version, log)
    record = caplog.records[0]
    assert msg in record.getMessage()
