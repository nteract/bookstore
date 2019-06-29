"""Handlers for Bookstore API"""
import json

from notebook.base.handlers import APIHandler
from notebook.base.handlers import path_regex
from .utils import url_path_join
from tornado import web

from ._version import __version__
from .bookstore_config import BookstoreSettings
from .bookstore_config import validate_bookstore
from .publish import BookstorePublishAPIHandler
from .clone import BookstoreCloneHandler, BookstoreCloneAPIHandler


version = __version__


class BookstoreVersionHandler(APIHandler):
    """Handler responsible for Bookstore version information

    Used to lay foundations for the bookstore package. Though, frontends can use this endpoint for feature detection.

    Methods
    -------
    get(self)
        Provides version info and feature availability based on serverside settings.
    build_response_dict(self)
        Helper to populate response.
    """

    @web.authenticated
    def get(self):
        """GET /api/bookstore/

        Returns version info and validation info for various bookstore features.
        """
        self.finish(json.dumps(self.build_response_dict()))

    def build_response_dict(self):
        """Helper for building the version handler's response before serialization."""
        return {
            "release": self.settings['bookstore']["release"],
            "features": self.settings['bookstore']["features"],
        }


def build_settings_dict(validation):
    """Helper for building the settings info that will be assigned to the web_app."""
    return {"release": version, "features": validation}


def load_jupyter_server_extension(nb_app):
    web_app = nb_app.web_app
    host_pattern = '.*$'

    base_url = web_app.settings['base_url']

    bookstore_settings = BookstoreSettings(parent=nb_app)
    validation = validate_bookstore(bookstore_settings)
    web_app.settings['bookstore'] = build_settings_dict(validation)
    handlers = collect_handlers(nb_app.log, base_url, validation)
    web_app.add_handlers(host_pattern, handlers)


def collect_handlers(log, base_url, validation):
    """Utility that collects bookstore endpoints & handlers to be added to the webapp.

    This uses bookstore feature validation to determine which endpoints should be enabled.
    It returns all valid pairs of endpoint patterns and handler classes. 

    Parameters
    ----------
    log : logging.Logger
      Log (usually from the NotebookApp) for logging endpoint changes.
    base_url: str
      The base_url to which we append routes.
    validation: dict
       Validation dictionary for determining which endpoints to enable.

    Returns
    --------
    
    List[Tuple[str, tornado.web.RequestHandler]]
      List of pairs of endpoint patterns and the handler used to handle requests at that endpoint.
    """
    base_bookstore_pattern = url_path_join(base_url, '/bookstore')
    base_bookstore_api_pattern = url_path_join(base_url, '/api/bookstore')

    handlers = []
    # Always enable the version handler for the API
    handlers.append((base_bookstore_api_pattern, BookstoreVersionHandler))

    if validation['publish_valid']:
        log.info(f"[bookstore] Enabling bookstore publishing, version: {version}")
        handlers.append(
            (
                url_path_join(base_bookstore_api_pattern, r"/publish%s" % path_regex),
                BookstorePublishAPIHandler,
            )
        )
    else:
        log.info("[bookstore] Publishing disabled. s3_bucket or endpoint are not configured.")

    if validation['clone_valid']:
        log.info(f"[bookstore] Enabling bookstore cloning, version: {version}")
        handlers.append(
            (url_path_join(base_bookstore_api_pattern, r"/clone(?:/?)*"), BookstoreCloneAPIHandler)
        ),
        handlers.append(
            (url_path_join(base_bookstore_pattern, r"/clone(?:/?)*"), BookstoreCloneHandler)
        )
    else:
        log.info(f"[bookstore] bookstore cloning disabled, version: {version}")

    return handlers
