import pytest

from bookstore.client.nb_client import (
    NotebookSession,
    KernelInfo,
    extract_kernel_id,
    LiveNotebookRecord,
)


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


def test_notebook_server_record(notebook_server_record, notebook_server_dict):
    assert notebook_server_record.base_url == notebook_server_dict['base_url']
    assert notebook_server_record.hostname == notebook_server_dict["hostname"]
    assert notebook_server_record.notebook_dir == notebook_server_dict["notebook_dir"]
    assert notebook_server_record.password == notebook_server_dict['password']
    assert notebook_server_record.pid == notebook_server_dict["pid"]
    assert notebook_server_record.port == notebook_server_dict["port"]
    assert notebook_server_record.secure == notebook_server_dict["secure"]
    assert notebook_server_record.token == notebook_server_dict["token"]
    assert notebook_server_record.url == notebook_server_dict["url"]
    assert notebook_server_record == LiveNotebookRecord(**notebook_server_dict)


def test_kernel_info_class(kernel_info_dict, kernel_info):
    assert kernel_info.id == kernel_info_dict['id']
    assert kernel_info.name == kernel_info_dict["name"]
    assert kernel_info.last_activity == kernel_info_dict["last_activity"]
    assert kernel_info.execution_state == kernel_info_dict['execution_state']
    assert kernel_info.connections == kernel_info_dict["connections"]
    assert kernel_info == KernelInfo(**kernel_info_dict)


def test_notebook_session_class(notebook_session, session_dict):
    # assert notebook_session.id == session_dict['id'] # TODO: once id is re-added to NotebookSession's attributes readd this
    assert notebook_session.path == session_dict["path"]
    assert notebook_session.name == session_dict["name"]
    assert notebook_session.type == session_dict['type']
    assert notebook_session.kernel == KernelInfo(**session_dict["kernel"])
    assert notebook_session.notebook == session_dict["notebook"]
    assert notebook_session == NotebookSession(**session_dict)


@pytest.mark.parametrize(
    "connection_file, expected_kernel_id",
    [
        (
            "kernel-f92b7c8b-0858-4d10-903c-b0631540fb36.json",
            "f92b7c8b-0858-4d10-903c-b0631540fb36",
        ),
        (
            "kernel-ee2b7c8b-0858-4d10-903c-b0631540fb36.json",
            "ee2b7c8b-0858-4d10-903c-b0631540fb36",
        ),
    ],
)
def test_extract_kernel_id(connection_file, expected_kernel_id):
    assert expected_kernel_id == extract_kernel_id(connection_file)
