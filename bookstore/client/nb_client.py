"""Client to test bookstore endpoints from within a notebook.


TODO: (Clarify) We want to test our bookstore endpoints, but it's no fun having
to do this in an insecure fashion. Better would be to have some security in
place.

Example
-------

[{'base_url': '/',
  'hostname': 'localhost',
  'notebook_dir': '/Users/mpacer/jupyter/eg_notebooks',
  'password': False,
  'pid': 96033,
  'port': 8888,
  'secure': False,
  'token': '',
  'url': 'http://localhost:8888/'}]
"""
import os
import re
import json
from copy import deepcopy
from typing import NamedTuple

import requests
from IPython import get_ipython
from notebook.notebookapp import list_running_servers


def extract_kernel_id(connection_file):
    connection_filename = os.path.basename(connection_file)
    kernel_id = re.sub(r"kernel-(.*)\.json", r"\1", connection_filename)
    return kernel_id


class LiveNotebookRecord(NamedTuple):
    """Representation of live notebook server.

    This is a record of an object returned by
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
        self.model = {
            "id": id,
            "name": name,
            "last_activity": last_activity,
            "execution_state": execution_state,
            "connections": connections,
        }
        self.id = id
        self.name = name
        self.last_activity = last_activity
        self.execution_state = execution_state
        self.connections = connections

    def __repr__(self):
        return json.dumps(self.model, indent=2)


class NotebookSession:  # (NamedTuple):
    #     id: str #'68d9c58f-c57d-4133-8b41-5ec2731b268d',
    #     path: str #'Untitled38.ipynb',
    #     name: str #'',
    #     type: str #'notebook',
    #     kernel: KernelInfo
    #     notebook: dict # deprecated API {'path': 'Untitled38.ipynb', 'name': ''}}}

    def __init__(self, *args, path, name, type, kernel, notebook, **kwargs):
        self.model = {
            "path": path,
            "name": name,
            "type": type,
            "kernel": kernel,
            "notebook": notebook,
        }
        self.path = path
        self.name = name
        self.type = type
        self.kernel = KernelInfo(**kernel)
        self.notebook = notebook

    def __repr__(self):
        return json.dumps(self.model, indent=2)


class NotebookClient:
    """Client used to interact with bookstore from within a running notebook UI"""

    def __init__(self, nb_config):
        self.nb_config = nb_config
        self.nb_record = LiveNotebookRecord(**self.nb_config)
        self.url = self.nb_record.url.rstrip(
            "/"
        )  # So that we can have full API endpoints without double //
        self.setup_auth()
        self.setup_request_sessions()

    def setup_auth(self):
        """ Sets up token access for authorizing requests to notebook server.

        This sets the notebook token as self.token and the xsrf_token as self.xsrf_token.
        """
        self.token = self.nb_record.token
        first = requests.get(f"{self.url}/login")
        self.xsrf_token = first.cookies.get("_xsrf", "")

    def setup_request_sessions(self):
        """ Sets up a requests.Session object for sharing headers across API requests.
        """
        self.req_session = requests.Session()
        self.req_session.headers.update(self.headers)

    @property
    def sessions(self):
        """Current notebook sessions. Reissues request on each call.
        """
        return {
            session['kernel']['id']: NotebookSession(**session) for session in self.get_sessions()
        }

    @property
    def headers(self):
        """Default headers to be shared across requests.
        """
        headers = {
            'Authorization': f'token {self.token}',
            'X-XSRFToken': self.xsrf_token,
            "Content-Type": "application/json",
        }
        return headers

    @property
    def sessions_endpoint(self):
        api_endpoint = "/api/sessions/"
        return f"{self.url}{api_endpoint}"

    def get_sessions(self):
        target_url = f"{self.sessions_endpoint}"
        resp = self.req_session.get(target_url)
        return resp.json()

    @property
    def kernels_endpoint(self):
        api_endpoint = "/api/kernels/"
        return f"{self.url}{api_endpoint}"

    def get_kernels(self):
        target_url = f"{self.kernels_endpoint}"
        resp = self.req_session.get(target_url)
        return resp.json()

    @property
    def kernels(self):
        return self.get_kernels()

    @property
    def contents_endpoint(self):
        api_endpoint = "/api/contents/"
        return f"{self.url}{api_endpoint}"

    def get_sessions(self):
        target_url = f"{self.sessions_endpoint}"
        resp = self.req_session.get(target_url)
        return resp.json()

    @property
    def contents_endpoint(self):
        api_endpoint = "/api/contents/"
        return f"{self.url}{api_endpoint}"

    def get_contents(self, path):
        target_url = f"{self.contents_endpoint}{path}"
        resp = self.req_session.get(target_url)
        return resp.json()


class NotebookClientCollection:
    """Representation of a collection of notebook clients"""

    # TODO: refactor from lambda to a def
    nb_client_gen = lambda: (NotebookClient(x) for x in list_running_servers())
    sessions = {x.url: x.sessions for x in nb_client_gen()}

    @classmethod
    def current_server(cls):
        """class method for current notebook server"""

        current_kernel_id = extract_kernel_id(get_ipython().parent.parent.connection_file)
        for server_url, session_dict in cls.sessions.items():
            for session_id, session in session_dict.items():
                if session.kernel.id == current_kernel_id:
                    return next(
                        client for client in cls.nb_client_gen() if client.url == server_url
                    )


class CurrentNotebookClient(NotebookClient):
    """Represents the currently active notebook client"""

    def __init__(self):
        self.nb_client = NotebookClientCollection.current_server()
        super().__init__(self.nb_client.nb_config)
        self.session = self.sessions[self.kernel_id]

    @property
    def connection_file(self):
        return get_ipython().parent.parent.connection_file

    @property
    def kernel_id(self):
        return extract_kernel_id(self.connection_file)
