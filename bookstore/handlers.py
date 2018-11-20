import json

from notebook.base.handlers import APIHandler
from notebook.utils import url_path_join
from tornado import web

from ._version import get_versions

version = get_versions()['version']


class BookstoreVersionHandler(APIHandler):
    """Returns the version of bookstore currently running. Used mostly to lay foundations
    for this package though frontends can use this endpoint for feature detection.
    """

    @web.authenticated
    def get(self):
        self.finish(json.dumps({"bookstore": True, "version": version}))


def load_jupyter_server_extension(nb_app):
    web_app = nb_app.web_app
    host_pattern = '.*$'
    base_bookstore_pattern = url_path_join(
        web_app.settings['base_url'], '/api/bookstore'
    )

    web_app.add_handlers(
        host_pattern, [(base_bookstore_pattern, BookstoreVersionHandler)]
    )
