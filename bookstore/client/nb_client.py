"""Client for accessing notebook server endpoints from within a notebook.
"""
import json
import os
import re
from copy import deepcopy
from typing import NamedTuple

import requests
from IPython import get_ipython
from notebook.notebookapp import list_running_servers


def extract_kernel_id(connection_file):
    """Get the kernel id string from a file"""
    # regex is used as a more robust approach than lstrip
    connection_filename = os.path.basename(connection_file)
    kernel_id = re.sub(r"kernel-(.*)\.json", r"\1", connection_filename)
    return kernel_id


class LiveNotebookRecord(NamedTuple):
    """Representation of live notebook server.

    This is a record of an object returned by
    `notebook.notebookapp.list_running_servers()`.

    Example
    -------
    :: 

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
    """Representation of kernel info returned by the notebook's /api/kernel endpoint.

    Attributes
    ----------
    id: str
    name: str
    last_activity: str
    execution_state: str 
    connections: int

    Example
    -------
    ::

        {id: 'f92b7c8b-0858-4d10-903c-b0631540fb36',
        name: 'dev',
        last_activity: '2019-03-14T23:38:08.137987Z',
        execution_state: 'idle',
        connections: 0}
    """

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

    def __eq__(self, other):
        if isinstance(other, KernelInfo):
            cmp_attrs = [
                self.id == other.id,
                self.name == other.name,
                self.last_activity == other.last_activity,
                self.execution_state == other.execution_state,
                self.connections == other.connections,
            ]
            return all(cmp_attrs)
        else:
            return False


class NotebookSession:
    """Representation of session info returned by the notebook's /api/sessions/ endpoint.
    
    Attributes
    ----------
    id: str
    path: str 
    name: str 
    type: str 
    kernel: KernelInfo
    notebook: dict 
    model: dict
        Record of the raw response (without converting the KernelInfo).

    Example
    -------
    ::
    
        {id: '68d9c58f-c57d-4133-8b41-5ec2731b268d',
         path: 'Untitled38.ipynb',
         name: '',
         type: 'notebook',
         kernel: KernelInfo(id='f92b7c8b-0858-4d10-903c-b0631540fb36', 
                            name='dev', 
                            last_activity='2019-03-14T23:38:08.137987Z', 
                            execution_state='idle', 
                            connections=0),
        notebook: {'path': 'Untitled38.ipynb', 'name': ''}}
    """

    def __init__(self, *args, path, name, type, kernel, notebook={}, **kwargs):
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

    def __eq__(self, other):
        if isinstance(other, NotebookSession):
            cmp_attrs = [
                # self.id == other.id,
                self.path == other.path,
                self.name == other.name,
                self.type == other.type,
                self.kernel == other.kernel,
                self.notebook == other.notebook,
            ]
            return all(cmp_attrs)
        else:
            return False


class NotebookClient:
    """EXPERIMENTAL SUPPORT: Client used to interact with a notebook server from within a notebook.

    Parameters
    ----------
    nb_config: dict
        Dictionary of info compatible with creating a LiveNotebookRecord.

    Attributes
    ----------
    nb_config: dict
       Dictionary of info compatible with creating a LiveNotebookRecord. 
    nb_record: LiveNotebookRecord
        LiveNotebookRecord of info for this notebook
    url: str
        url from nb_record minus final /
    token: str
        token used for authenticating requests serverside
    xsrf_token: str
        xsrf_token used in cookie for authenticating requests
    req_session: requests.Session
        Session to be reused across methods
    """

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
        """ Sets up a requests.Session object for sharing headers across API requests. """
        self.req_session = requests.Session()
        self.req_session.headers.update(self.headers)

    @property
    def sessions(self):
        """Current notebook sessions. Reissues request on each call. """
        return {
            session['kernel']['id']: NotebookSession(**session) for session in self.get_sessions()
        }

    @property
    def headers(self):
        """Default headers to be shared across requests. """
        headers = {
            'Authorization': f'token {self.token}',
            'X-XSRFToken': self.xsrf_token,
            "Content-Type": "application/json",
        }
        return headers

    @property
    def sessions_endpoint(self):
        """Current server's kernels API endpoint."""
        api_endpoint = "/api/sessions/"
        return f"{self.url}{api_endpoint}"

    def get_sessions(self):
        """Requests info about current sessions from notebook server."""
        target_url = f"{self.sessions_endpoint}"
        resp = self.req_session.get(target_url)
        return resp.json()

    @property
    def kernels_endpoint(self):
        """Current server's kernels API endpoint."""
        api_endpoint = "/api/kernels/"
        return f"{self.url}{api_endpoint}"

    def get_kernels(self):
        """Requests info about current kernels from notebook server."""
        target_url = f"{self.kernels_endpoint}"
        resp = self.req_session.get(target_url)
        return resp.json()

    @property
    def kernels(self):
        """Current notebook kernels. Reissues request on each call."""
        return self.get_kernels()

    @property
    def contents_endpoint(self):
        """Current server's contents API endpoint."""
        api_endpoint = "/api/contents/"
        return f"{self.url}{api_endpoint}"

    def get_contents(self, path):
        """Requests info about current contents from notebook server."""
        target_url = f"{self.contents_endpoint}{path}"
        resp = self.req_session.get(target_url)
        return resp.json()


class NotebookClientCollection:
    """EXPERIMENTAL SUPPORT: Representation of a collection of notebook clients"""

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
    """EXPERIMENTAL SUPPORT: Represents the currently active notebook client."""

    def __init__(self):
        self.nb_client = NotebookClientCollection.current_server()
        super().__init__(self.nb_client.nb_config)
        self.session = self.sessions[self.kernel_id]

    @property
    def connection_file(self):
        """Connection file for connecting to current notebook's kernel."""
        return get_ipython().parent.parent.connection_file

    @property
    def kernel_id(self):
        """Kernel id for identifying which notebook is currently being used by this session."""
        return extract_kernel_id(self.connection_file)
