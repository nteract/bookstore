# # Building a Notebook client
#
# We want to test our bookstore endpoints, but it's no fun having to do this in an insecure fashion. Better would be to have some security in place.
#
#
# ## Example notebook config
#
#
# ```
# [{'base_url': '/',
#   'hostname': 'localhost',
#   'notebook_dir': '/Users/mpacer/jupyter/eg_notebooks',
#   'password': False,
#   'pid': 96033,
#   'port': 8888,
#   'secure': False,
#   'token': '',
#   'url': 'http://localhost:8888/'}]
# ```

import os

import requests

from copy import deepcopy
from typing import NamedTuple


from notebook.notebookapp import list_running_servers


def extract_kernel_id(connection_file):
    return os.path.basename(connection_file).lstrip('kernel-').rstrip('.json')


class LiveNotebookRecord(NamedTuple):
    """Representation of live notebook server

    This is a realization of the object returned by
    `notebook.notebookapp.list_running_servers()`.
    """

    base_url: str
    hostname: str
    notebook_dir: str
    password: bool
    pid: int
    port: int
    secure: bool
    token: str
    url: str


class KernelInfo:
    #     id: str # 'f92b7c8b-0858-4d10-903c-b0631540fb36',
    #     name: str # 'dev',
    #     last_activity: str #'2019-03-14T23:38:08.137987Z',
    #     execution_state: str #'idle',
    #     connections: int # 0
    def __init__(self, *args, id, name, last_activity, execution_state, connections):
        self.id = id
        self.name = name
        self.last_activity = last_activity
        self.execution_state = execution_state
        self.connections = connections


class NotebookSession:  # (NamedTuple):
    #     id: str #'68d9c58f-c57d-4133-8b41-5ec2731b268d',
    #     path: str #'Untitled38.ipynb',
    #     name: str #'',
    #     type: str #'notebook',
    #     kernel: KernelInfo
    #     notebook: dict # {'path': 'Untitled38.ipynb', 'name': ''}}}

    def __init__(self, *args, path, name, type, kernel, notebook, **kwargs):
        self.path = path
        self.name = name
        self.type = type
        self.kernel = KernelInfo(**kernel)
        self.notebook = notebook


class NotebookClient:
    def __init__(self, nb_config):
        self.nb_config = nb_config
        self.nb_record = LiveNotebookRecord(**self.nb_config)
        self.url = self.nb_record.url.rstrip(
            "/"
        )  # So that we can have full API endpoints without double //
        self.token = self.nb_record.token
        sessions_temp = self.get_sessions()
        self.sessions = {session['kernel']['id']: session for session in sessions_temp}

    @property
    def sessions_endpoint(self):
        api_endpoint = "/api/sessions/"
        return f"{self.url}{api_endpoint}"

    def get_sessions(self):
        target_url = f"{self.sessions_endpoint}"
        headers = {'Authorization': f'token {self.token}'}
        resp = requests.get(target_url, headers=headers)
        return resp.json()

    @property
    def kernels_endpoint(self):
        api_endpoint = "/api/kernels/"
        return f"{self.url}{api_endpoint}"

    def get_kernels(self):
        target_url = f"{self.sessions_endpoint}"
        headers = {'Authorization': f'token {self.token}'}
        resp = requests.get(target_url, headers=headers)
        return resp.json()

    @property
    def contents_endpoint(self):
        api_endpoint = "/api/contents/"
        return f"{self.url}{api_endpoint}"

    def get_contents(self, path):
        target_url = f"{self.contents_endpoint}{path}"
        headers = {'Authorization': f'token {self.token}'}
        resp = requests.get(target_url, headers=headers)
        return resp.json()


def python_compat_session(session):
    deepcopy(session)


class NotebookClientCollection:
    nb_client_gen = lambda: (NotebookClient(x) for x in list_running_servers())
    sessions = {x.url: x.sessions for x in nb_client_gen()}

    @classmethod
    def current_server(cls):
        for server_url, session_dict in cls.sessions.items():
            for session_id, session in session_dict.items():
                python_compat_session(session)
                if NotebookSession(**session).kernel.id == extract_kernel_id(
                    get_ipython().parent.parent.connection_file
                ):
                    #                 if session['kernel']['id'] == extract_kernel_id(get_ipython().parent.parent.connection_file):

                    return next(
                        client for client in cls.nb_client_gen() if client.url == server_url
                    )


class CurrentNotebookClient(NotebookClient):
    def __init__(self):
        self.nb_client = NotebookClientCollection.current_server()
        super().__init__(self.nb_client.nb_config)
        self.session = self.sessions[self.kernel_id]
        self.notebook = NotebookSession(**self.session).notebook

    @property
    def connection_file(self):
        return get_ipython().parent.parent.connection_file

    @property
    def kernel_id(self):
        return os.path.basename(self.connection_file).lstrip('kernel-').rstrip('.json')
