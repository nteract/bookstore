from notebook.services.contents.filemanager import FileContentsManager
from traitlets import Unicode
from pprint import pprint

import nbformat 

from .bookstore_config import Bookstore


from traitlets import (
    Any,
    Bool,
    Dict,
    Instance,
    List,
    TraitError,
    Type,
    Unicode,
    validate,
    default,
)


class BookstoreContentsArchiver(FileContentsManager):
    """
    Archives contents via one ContentsManager and passes through to
    another ContentsManager.

    Likely route:

    * Write directly to S3 on post_save_hook

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.bookstore = Bookstore(parent=self)
    
    def run_pre_save_hook(self, model, path, **kwargs):
        """Override the direct pre_save_hook to implement our own without monkey patching
        """
        pprint(self.bookstore._trait_values)
        pprint(self.bookstore.storage_settings._trait_values)

        if model['type'] != 'notebook':
            return

        notebook = nbformat.from_dict(model['content'])

        # write to S3 asynchronously
        # store the hash

        print(notebook)
