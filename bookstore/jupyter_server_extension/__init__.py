from .handlers import load_jupyter_server_extension

def _jupyter_server_extension_paths():
    return [dict(module="bookstore")]
