import pytest

from bookstore.utils import url_path_join


def test_url_join_pieces():
    bucket = 'mybucket'
    prefix = 'yo'
    path = 'pickles'
    assert url_path_join(bucket, prefix, path) == 'mybucket/yo/pickles'


def test_url_join_no_pieces():
    with pytest.raises(IndexError):
        url_path_join()


def test_url_join_one_piece():
    assert url_path_join('mypath') == 'mypath'


def test_url_path_join_strip_slash():
    assert url_path_join('/bucket/', 'yo', 'pickles/') == '/bucket/yo/pickles/'
    assert url_path_join('bucket/', '/yo/', '/pickles') == 'bucket/yo/pickles'
    assert url_path_join('/bucket/', '/yo/', '/pickles/') == '/bucket/yo/pickles/'
    assert url_path_join('/', '/') == '/'
