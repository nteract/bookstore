import asyncio
import pytest

from bookstore.publish import BookstorePublishAPIHandler


def test_create_publish_handler_no_params():
    with pytest.raises(TypeError):
        assert BookstorePublishAPIHandler()
