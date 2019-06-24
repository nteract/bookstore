import pytest

from bookstore.client.nb_client import (
    NotebookSession,
    KernelInfo,
    extract_kernel_id,
    LiveNotebookRecord,
)

from bookstore.tests.client.client_fixtures import *


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
    assert extract_kernel_id(connection_file) == expected_kernel_id
