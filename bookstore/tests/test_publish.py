import asyncio
import pytest

from bookstore.publish import BookstorePublishHandler


def test_create_publish_handler_no_params():
    with pytest.raises(TypeError):
        assert BookstorePublishHandler()
