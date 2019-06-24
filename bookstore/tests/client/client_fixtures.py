import pytest

from bookstore.client.nb_client import NotebookSession, KernelInfo, LiveNotebookRecord


@pytest.fixture
def notebook_server_dict():
    notebook_server_dict = {
        "base_url": "/",
        "hostname": "localhost",
        "notebook_dir": "/Users/username",
        "password": False,
        "pid": 20981,
        "port": 8888,
        "secure": False,
        "token": "e5814788aeef225172364fcdf1240b90729169a2ced375c7",
        "url": "http://localhost:8888/",
    }
    return notebook_server_dict


@pytest.fixture
def notebook_server_record(notebook_server_dict):
    notebook_server_record = LiveNotebookRecord(**notebook_server_dict)
    return notebook_server_record


@pytest.fixture(scope="module")
def kernel_info_dict():
    info_dict = {
        "id": 'f92b7c8b-0858-4d10-903c-b0631540fb36',
        "name": 'dev',
        "last_activity": '2019-03-14T23:38:08.137987Z',
        "execution_state": 'idle',
        "connections": 0,
    }
    return info_dict


@pytest.fixture(scope="module")
def kernel_info(kernel_info_dict):
    kernel_info = KernelInfo(**kernel_info_dict)
    return kernel_info


@pytest.fixture
def session_dict(kernel_info_dict):
    session_dict = {
        "id": '68d9c58f-c57d-4133-8b41-5ec2731b268d',
        "path": 'Untitled38.ipynb',
        "name": '',
        "type": 'notebook',
        "kernel": kernel_info_dict,
        "notebook": {'path': 'Untitled38.ipynb', 'name': ''},  # deprecated API
    }
    return session_dict


@pytest.fixture
def notebook_session(session_dict):
    notebook_session = NotebookSession(**session_dict)
    return notebook_session
