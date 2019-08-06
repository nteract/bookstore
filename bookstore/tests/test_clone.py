import json
import logging
import uuid
import os

from unittest.mock import Mock
from pathlib import Path

import pytest
import nbformat

from jinja2 import Environment
from notebook.services.contents.filemanager import FileContentsManager
from tornado.testing import AsyncTestCase, gen_test
from tornado.web import Application, HTTPError
from tornado.httpserver import HTTPRequest
from traitlets.config import Config

from bookstore.bookstore_config import BookstoreSettings
from bookstore.clone import (
    build_notebook_model,
    build_file_model,
    BookstoreCloneHandler,
    BookstoreCloneAPIHandler,
    validate_relpath,
    BookstoreFSCloneHandler,
    BookstoreFSCloneAPIHandler,
)
from bookstore.utils import TemporaryWorkingDirectory

from . import test_dir


log = logging.getLogger('test_clone')


def test_build_notebook_model():
    content = nbformat.v4.new_notebook()
    expected = {
        "type": "notebook",
        "format": "json",
        "content": content,
        "name": "my_notebook_name.ipynb",
        "path": "test_directory/my_notebook_name.ipynb",
    }
    path = "./test_directory/my_notebook_name.ipynb"
    nb_content = nbformat.writes(content)
    assert build_notebook_model(nb_content, path) == expected


def test_build_file_model():
    content = "my fancy file"
    expected = {
        "type": "file",
        "format": "text",
        "content": content,
        "name": "file_name.txt",
        "path": "test_directory/file_name.txt",
    }
    path = "./test_directory/file_name.txt"
    assert build_file_model(content, path) == expected


class TestCloneHandler(AsyncTestCase):
    def setUp(self):
        super().setUp()
        self.mock_application = Mock(
            spec=Application, ui_methods={}, ui_modules={}, settings={'jinja2_env': Environment()}
        )

    def get_handler(self, uri, app=None):
        if app is None:
            app = self.mock_application
        connection = Mock(context=Mock(protocol="https"))
        payload_request = HTTPRequest(
            method='GET',
            uri=uri,
            headers={"Host": "localhost:8888"},
            body=None,
            connection=connection,
        )
        return BookstoreCloneHandler(app, payload_request)

    @gen_test
    async def test_get_no_param(self):
        empty_handler = self.get_handler('/bookstore/clone')
        with pytest.raises(HTTPError):
            await empty_handler.get()

    @gen_test
    async def test_get_no_bucket(self):
        no_bucket_handler = self.get_handler('/bookstore/clone?s3_bucket=&s3_key=hi')
        with pytest.raises(HTTPError):
            await no_bucket_handler.get()

    @gen_test
    async def test_get_no_object_key(self):
        no_object_key_handler = self.get_handler('/bookstore/clone?s3_bucket=hello&s3_key=')
        with pytest.raises(HTTPError):
            await no_object_key_handler.get()

    @gen_test
    async def test_get_success(self):
        success_handler = self.get_handler('/bookstore/clone?s3_bucket=hello&s3_key=my_key')
        await success_handler.get()

    def test_gen_template_params(self):
        success_handler = self.get_handler('/bookstore/clone?s3_bucket=hello&s3_key=my_key')
        expected = {
            'post_model': {'s3_bucket': 'hello', 's3_key': 'my_key'},
            'clone_api_url': 'https://localhost:8888/api/bookstore/clone',
            'redirect_contents_url': 'https://localhost:8888',
            'source_description': "'my_key' from the s3 bucket 'hello'",
        }
        success_handler = self.get_handler('/bookstore/clone?s3_bucket=hello&s3_key=my_key')
        output = success_handler.construct_template_params(
            s3_bucket="hello", s3_object_key="my_key"
        )
        assert expected == output

    def test_gen_template_params_base_url(self):
        base_url_list = ['/my_base_url', '/my_base_url/', 'my_base_url/', 'my_base_url']
        expected = {
            'post_model': {'s3_bucket': 'hello', 's3_key': 'my_key'},
            'clone_api_url': 'https://localhost:8888/my_base_url/api/bookstore/clone',
            'redirect_contents_url': 'https://localhost:8888',
            'source_description': "'my_key' from the s3 bucket 'hello'",
        }
        for base_url in base_url_list:
            mock_app = Mock(
                spec=Application,
                ui_methods={},
                ui_modules={},
                settings={'jinja2_env': Environment(), "base_url": base_url},
            )

            success_handler = self.get_handler(
                '/bookstore/clone?s3_bucket=hello&s3_key=my_key', app=mock_app
            )
            output = success_handler.construct_template_params(
                s3_bucket="hello", s3_object_key="my_key"
            )
            assert expected == output


class TestCloneAPIHandler(AsyncTestCase):
    def setUp(self):
        super().setUp()
        mock_settings = {
            "BookstoreSettings": {
                "s3_access_key_id": "mock_id",
                "s3_secret_access_key": "mock_access",
            }
        }
        config = Config(mock_settings)

        self.mock_application = Mock(
            spec=Application,
            ui_methods={},
            ui_modules={},
            settings={
                'jinja2_env': Environment(),
                "config": config,
                "contents_manager": FileContentsManager(),
            },
        )

    def post_handler(self, body_dict, app=None):
        if app is None:
            app = self.mock_application
        body = json.dumps(body_dict).encode('utf-8')
        payload_request = HTTPRequest(
            method='POST', uri="/api/bookstore/clone", headers=None, body=body, connection=Mock()
        )
        return BookstoreCloneAPIHandler(app, payload_request)

    @gen_test
    async def test_post_no_body(self):
        post_body_dict = {}
        empty_handler = self.post_handler(post_body_dict)
        with pytest.raises(HTTPError):
            await empty_handler.post()

    @gen_test
    async def test_post_empty_bucket(self):
        post_body_dict = {"s3_key": "my_key", "s3_bucket": ""}
        empty_bucket_handler = self.post_handler(post_body_dict)
        with pytest.raises(HTTPError):
            await empty_bucket_handler.post()

    @gen_test
    async def test_post_empty_key(self):
        post_body_dict = {"s3_key": "", "s3_bucket": "my_bucket"}
        empty_key_handler = self.post_handler(post_body_dict)
        with pytest.raises(HTTPError):
            await empty_key_handler.post()

    @gen_test
    async def test_post_nonsense_params(self):
        post_body_dict = {"s3_key": "my_key", "s3_bucket": "my_bucket"}
        success_handler = self.post_handler(post_body_dict)
        with pytest.raises(HTTPError):
            await success_handler.post()

    @gen_test
    async def test_private_clone_nonsense_params(self):
        s3_bucket = "my_key"
        s3_object_key = "my_bucket"
        post_body_dict = {"s3_key": s3_object_key, "s3_bucket": s3_bucket}
        success_handler = self.post_handler(post_body_dict)
        with pytest.raises(HTTPError):
            await success_handler._clone(s3_bucket, s3_object_key)

    def test_build_post_response_model(self):
        content = "some arbitrary content"
        expected = {
            "type": "file",
            "format": "text",
            "content": content,
            "name": "file_name.txt",
            "path": "test_directory/file_name.txt",
            "s3_path": "s3://my_bucket/original_key/may_be_different_than_storage.txt",
            'versionID': "eeee222eee",
        }

        s3_bucket = "my_bucket"
        s3_object_key = "original_key/may_be_different_than_storage.txt"
        obj = {'VersionId': "eeee222eee"}
        model = {
            "type": "file",
            "format": "text",
            "content": content,
            "name": "file_name.txt",
            "path": "test_directory/file_name.txt",
        }
        handler = self.post_handler({})
        actual = handler.build_post_response_model(model, obj, s3_bucket, s3_object_key)
        assert actual == expected

    @gen_test
    async def test_build_text_content_model(self):
        content = "some content"
        expected = {
            "type": "file",
            "format": "text",
            "content": content,
            "name": "file_name.txt",
            "path": "test_directory/file_name.txt",
        }

        path = "test_directory/file_name.txt"
        success_handler = self.post_handler({})
        model = success_handler.build_content_model(content, path)
        assert model == expected

    @gen_test
    async def test_build_notebook_content_model(self):
        content = nbformat.v4.new_notebook()
        expected = {
            "type": "notebook",
            "format": "json",
            "content": content,
            "name": "file_name.ipynb",
            "path": "test_directory/file_name.ipynb",
        }

        str_content = nbformat.writes(content)

        path = "test_directory/file_name.ipynb"
        success_handler = self.post_handler({})
        model = success_handler.build_content_model(str_content, path)
        assert model == expected


def test_validate_relpath():
    relpath = 'hi'
    settings = BookstoreSettings(fs_cloning_basedir="/anything")
    fs_clonepath = validate_relpath(relpath, settings, log)
    assert fs_clonepath == Path("/anything/hi")


def test_validate_relpath_empty_relpath(caplog):
    relpath = ''
    settings = BookstoreSettings(fs_cloning_basedir="/anything")
    with pytest.raises(HTTPError):
        with caplog.at_level(logging.INFO):
            fs_clonepath = validate_relpath(relpath, settings, log)
    assert "Request received with empty relpath." in caplog.text


def test_validate_relpath_escape_basedir(caplog):
    relpath = '../hi'
    settings = BookstoreSettings(fs_cloning_basedir="/anything")
    with pytest.raises(HTTPError):
        with caplog.at_level(logging.INFO):
            fs_clonepath = validate_relpath(relpath, settings, log)
    assert f"Request to clone from a path outside of base directory" in caplog.text


class TestFSCloneHandler(AsyncTestCase):
    def setUp(self):
        super().setUp()
        mock_settings = {"BookstoreSettings": {"fs_cloning_basedir": test_dir}}
        self.config = Config(mock_settings)
        self.mock_application = Mock(
            spec=Application,
            ui_methods={},
            ui_modules={},
            settings={'jinja2_env': Environment(), 'config': self.config},
        )

    def get_handler(self, uri, app=None):
        if app is None:
            app = self.mock_application
        connection = Mock(context=Mock(protocol="https"))
        payload_request = HTTPRequest(
            method='GET',
            uri=uri,
            headers={"Host": "localhost:8888"},
            body=None,
            connection=connection,
        )
        return BookstoreFSCloneHandler(app, payload_request)

    @gen_test
    async def test_get_no_param(self):
        empty_handler = self.get_handler('/bookstore/fs-clone')
        with pytest.raises(HTTPError):
            await empty_handler.get()

    @gen_test
    async def test_get_empty_relpath(self):
        empty_relpath_handler = self.get_handler('/bookstore/fs-clone?relpath=')
        with pytest.raises(HTTPError):
            await empty_relpath_handler.get()

    @gen_test
    async def test_get_escape_basedir(self):
        escape_basedir_handler = self.get_handler('/bookstore/fs-clone?relpath=../hi')
        with pytest.raises(HTTPError):
            await escape_basedir_handler.get()

    @gen_test
    async def test_get_success(self):
        success_handler = self.get_handler('/bookstore/fs-clone?relpath=my/test/path.ipynb')
        await success_handler.get()

    def test_gen_template_params(self):
        expected = {
            'post_model': {'relpath': 'my/test/path.ipynb'},
            'clone_api_url': 'https://localhost:8888/api/bookstore/fs-clone',
            'redirect_contents_url': 'https://localhost:8888',
            'source_description': '/Users/jupyter/my/test/path.ipynb',
        }
        success_handler = self.get_handler('/bookstore/fs-clone?relpath=my/test/path.ipynb')
        output = success_handler.construct_template_params(
            relpath='my/test/path.ipynb', fs_clonepath='/Users/jupyter/my/test/path.ipynb'
        )
        assert expected == output

    def test_gen_template_params_base_url(self):
        base_url_list = ['/my_base_url', '/my_base_url/', 'my_base_url/', 'my_base_url']
        expected = {
            'post_model': {'relpath': 'my/test/path.ipynb'},
            'clone_api_url': 'https://localhost:8888/my_base_url/api/bookstore/fs-clone',
            'redirect_contents_url': 'https://localhost:8888',
            'source_description': '/Users/jupyter/my/test/path.ipynb',
        }
        for base_url in base_url_list:
            mock_app = Mock(
                spec=Application,
                ui_methods={},
                ui_modules={},
                settings={'jinja2_env': Environment(), "base_url": base_url, "config": self.config},
            )

            success_handler = self.get_handler(
                '/bookstore/fs-clone?relpath=my/test/path.ipynb', app=mock_app
            )
            output = success_handler.construct_template_params(
                relpath='my/test/path.ipynb', fs_clonepath='/Users/jupyter/my/test/path.ipynb'
            )
            assert expected == output


class TestFSCloneAPIHandler(AsyncTestCase):
    def setUp(self):
        super().setUp()
        mock_settings = {
            "BookstoreSettings": {"fs_cloning_basedir": os.path.join(test_dir, 'test_files')}
        }
        config = Config(mock_settings)

        self.mock_application = Mock(
            spec=Application,
            ui_methods={},
            ui_modules={},
            settings={
                'jinja2_env': Environment(),
                "config": config,
                "contents_manager": FileContentsManager(),
            },
        )

    def post_handler(self, body_dict, app=None):
        if app is None:
            app = self.mock_application
        body = json.dumps(body_dict).encode('utf-8')
        payload_request = HTTPRequest(
            method='POST', uri="/api/bookstore/fs-clone", headers=None, body=body, connection=Mock()
        )
        return BookstoreFSCloneAPIHandler(app, payload_request)

    @gen_test
    async def test_post_no_body(self):
        post_body_dict = {}
        empty_handler = self.post_handler(post_body_dict)
        with pytest.raises(HTTPError):
            await empty_handler.post()

    @gen_test
    async def test_post_empty_relpath(self):
        post_body_dict = {"relpath": ""}
        empty_relpath_handler = self.post_handler(post_body_dict)
        with pytest.raises(HTTPError):
            await empty_relpath_handler.post()

    @gen_test
    async def test_post_basedir_escape(self):
        post_body_dict = {"relpath": "../myfile.txt"}
        empty_relpath_handler = self.post_handler(post_body_dict)
        with pytest.raises(HTTPError):
            await empty_relpath_handler.post()

    @gen_test
    async def test_post_nonsense_params(self):
        post_body_dict = {"relpath": str(uuid.uuid4())}
        success_handler = self.post_handler(post_body_dict)
        with pytest.raises(HTTPError):
            await success_handler.post()

    @gen_test
    async def test_post_success_notebook(self):
        post_body_dict = {"relpath": 'EmptyNotebook.ipynb'}
        with open(os.path.join(test_dir, 'test_files/EmptyNotebook.ipynb'), 'r') as f:
            expected = json.load(f)
        success_handler = self.post_handler(post_body_dict)
        setattr(success_handler, '_transforms', [])

        with TemporaryWorkingDirectory() as tmp:
            await success_handler.post()
            with open('EmptyNotebook.ipynb') as f:
                actual = json.load(f)
        assert actual == expected

    @gen_test
    async def test_build_text_content_model(self):
        content = "some content"
        expected = {
            "type": "file",
            "format": "text",
            "content": content,
            "name": "file_name.txt",
            "path": "test_directory/file_name.txt",
        }

        path = "test_directory/file_name.txt"
        post_handler = self.post_handler({})
        model = post_handler.build_content_model(content, path)
        assert model == expected

    @gen_test
    async def test_build_notebook_content_model(self):
        content = nbformat.v4.new_notebook()
        expected = {
            "type": "notebook",
            "format": "json",
            "content": content,
            "name": "file_name.ipynb",
            "path": "test_directory/file_name.ipynb",
        }

        str_content = nbformat.writes(content)

        path = "test_directory/file_name.ipynb"
        post_handler = self.post_handler({})
        model = post_handler.build_content_model(str_content, path)
        assert model == expected
