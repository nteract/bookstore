import os

PACKAGE_DIR: str = os.path.realpath(os.path.dirname(__file__))

del os

from .archive import BookstoreContentsArchiver
from .bookstore_config import BookstoreSettings
from .handlers import load_jupyter_server_extension
from ._version import __version__
from ._version import version_info


def _jupyter_server_extension_paths():
    return [dict(module="bookstore")]
