# TODO: refactor the import, PACKAGE_DIR, del
import os

from ._version import __version__, version_info
from .archive import BookstoreContentsArchiver
from .bookstore_config import BookstoreSettings
from .handlers import load_jupyter_server_extension

PACKAGE_DIR: str = os.path.realpath(os.path.dirname(__file__))

del os


def _jupyter_server_extension_paths():
    return [dict(module="bookstore")]
