import pytest

from bookstore.client.nb_client import (
    NotebookSession,
    KernelInfo,
)


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
