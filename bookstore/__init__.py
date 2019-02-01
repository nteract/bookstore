from .archive import BookstoreContentsArchiver
from .bookstore_config import BookstoreSettings
from .handlers import load_jupyter_server_extension
from ._version import version_info, __version__


def _jupyter_server_extension_paths():
    return [dict(module="bookstore")]
