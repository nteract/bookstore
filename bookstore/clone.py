import json

import aiobotocore

from notebook.base.handlers import APIHandler, path_regex
from notebook.utils import url_path_join
from tornado import web

from .s3_paths import s3_path, s3_key, s3_display_path
from .bookstore_config import BookstoreSettings


class BookstoreCloneHandler(APIHandler):
    """Clone a notebook from s3."""

    def post(self, path=''):
        """Clone a notebook to a given path.
        
        The payload for this should match that of the contents API for POST.
        
        Also, you could … *not* do that while still prototyping.
        That's ok! 
        But this all should go away.
        """
        self.log.info("About to clone to %s", path)

        if path == '' or path == '/':
            raise web.HTTPError(400, "Must have a path to publish to")

        model = self.get_json_body()
        
        self.log.info(model)

