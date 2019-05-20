"""Handlers for Bookstore API"""
import json

from notebook.base.handlers import APIHandler
from notebook.base.handlers import path_regex
from .utils import url_path_join
from tornado import web

from ._version import __version__
from .bookstore_config import BookstoreSettings
from .bookstore_config import validate_bookstore
from .publish import BookstorePublishHandler
from .clone import BookstoreCloneHandler


version = __version__


class BookstoreVersionHandler(APIHandler):
    """Handler responsible for Bookstore version information

    Used to lay foundations for the bookstore package. Though, frontends can use this endpoint for feature detection.
    """

    @web.authenticated
    def get(self):
        self.finish(
            json.dumps(
                {
                    "bookstore": True,
                    "version": self.settings['bookstore']["version"],
                    "validation": self.settings['bookstore']["validation"],
                }
            )
        )


# TODO: Add a check. Note: We need to ensure that publishing is not configured if bookstore settings are not
#       set. Because of how the APIHandlers cannot be configurable, all we can do is reach into settings
#       For applications this will mean checking the config and then applying it in


def load_jupyter_server_extension(nb_app):
    web_app = nb_app.web_app
    host_pattern = '.*$'

    # Always enable the version handler
    base_bookstore_pattern = url_path_join(web_app.settings['base_url'], '/api/bookstore')
    web_app.add_handlers(host_pattern, [(base_bookstore_pattern, BookstoreVersionHandler)])
    bookstore_settings = BookstoreSettings(parent=nb_app)
    web_app.settings['bookstore'] = {
        "version": version,
        "validation": validate_bookstore(bookstore_settings),
    }

    check_published = [
        web_app.settings['bookstore']['validation'].get("bookstore_valid"),
        web_app.settings['bookstore']['validation'].get("publish_valid"),
    ]

    if not all(check_published):
        nb_app.log.info("[bookstore] Not enabling bookstore publishing, endpoint not configured")
    else:
        nb_app.log.info(f"[bookstore] Enabling bookstore publishing, version: {version}")
        web_app.add_handlers(
            host_pattern,
            [
                (
                    url_path_join(base_bookstore_pattern, r"/published%s" % path_regex),
                    BookstorePublishHandler,
                )
            ],
        )

    web_app.add_handlers(
        host_pattern,
        [(url_path_join(base_bookstore_pattern, r"/cloned(?:/?)*"), BookstoreCloneHandler)],
    )
