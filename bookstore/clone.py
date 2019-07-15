"""Handler to clone notebook from storage."""
import json
import os

from copy import deepcopy

import aiobotocore

from botocore.exceptions import ClientError
from jinja2 import FileSystemLoader
from notebook.base.handlers import IPythonHandler, APIHandler
from tornado import web

from . import PACKAGE_DIR
from .bookstore_config import BookstoreSettings
from .s3_paths import s3_path, s3_display_path
from .utils import url_path_join

BOOKSTORE_FILE_LOADER = FileSystemLoader(PACKAGE_DIR)


def build_notebook_model(content, path):
    """Helper that builds a Contents API compatible model for notebooks.

    Parameters
    ----------
    content : str
        The content of the model.
    path : str
        The path to be targeted.

    Returns
    --------
    dict
        Jupyter Contents API compatible model for notebooks
    """
    model = {
        "type": "notebook",
        "format": "json",
        "content": json.loads(content),
        "name": os.path.basename(os.path.relpath(path)),
        "path": os.path.relpath(path),
    }
    return model


def build_file_model(content, path):
    """Helper that builds a Contents API compatible model for files.

    Parameters
    ----------
    content: str
        The content of the model
    path : str
        The path to be targeted.

    Returns
    --------
    dict
        Jupyter Contents API compatible model for files
    """
    model = {
        "type": "file",
        "format": "text",
        "content": content,
        "name": os.path.basename(os.path.relpath(path)),
        "path": os.path.relpath(path),
    }
    return model


class BookstoreCloneHandler(IPythonHandler):
    """Prepares and provides clone options page, populating UI with clone option parameters.

    Provides handling for ``GET`` requests when cloning a notebook
    from storage (S3). Launches a user interface with cloning options.

    Methods
    -------
    initialize(self)
        Helper to access bookstore settings.
    get(self)
        Checks for valid storage settings and render a UI for clone options.
    construct_template_params(self, s3_bucket, s3_object_key)
        Helper to populate Jinja template for cloning option page.
    get_template(self, name)
        Loads a Jinja template and its related settings.

    See also
    --------
    `Jupyter Notebook reference on Custom Handlers <https://jupyter-notebook.readthedocs.io/en/stable/extending/handlers.html#registering-custom-handlers>`_
    """

    def initialize(self):
        """Helper to retrieve bookstore setting for the session."""
        self.bookstore_settings = BookstoreSettings(config=self.config)

    @web.authenticated
    async def get(self):
        """GET /bookstore/clone?s3_bucket=<your_s3_bucket>&s3_key=<your_s3_key>

        Renders an options page that will allow you to clone a notebook
        from a specific bucket via the Bookstore cloning API.

        s3_bucket is the bucket you wish to clone from.
        s3_key is the object key that you wish to clone.
        """
        s3_bucket = self.get_argument("s3_bucket")
        if s3_bucket == '' or s3_bucket == "/":
            raise web.HTTPError(400, "Requires an S3 bucket in order to clone")

        # s3_paths module has an s3_key function; s3_object_key avoids confusion
        s3_object_key = self.get_argument("s3_key")
        if s3_object_key == '' or s3_object_key == '/':
            raise web.HTTPError(400, "Requires an S3 object key in order to clone")

        self.log.info(f"Setting up cloning landing page for {s3_object_key}")

        template_params = self.construct_template_params(s3_bucket, s3_object_key)
        self.set_header('Content-Type', 'text/html')
        self.write(self.render_template('clone.html', **template_params))

    def construct_template_params(self, s3_bucket, s3_object_key):
        """Helper that takes valid S3 parameters and populates UI template
        
        Returns
        --------
        
        dict
            Template parameters in a dictionary
        """
        base_uri = f"{self.request.protocol}://{self.request.host}"
        clone_api_url = url_path_join(base_uri, self.base_url, "/api/bookstore/clone")
        redirect_contents_url = url_path_join(base_uri, self.default_url)
        template_params = {
            "s3_bucket": s3_bucket,
            "s3_key": s3_object_key,
            "clone_api_url": clone_api_url,
            "redirect_contents_url": redirect_contents_url,
        }
        return template_params

    def get_template(self, name):
        """Loads a Jinja template by name."""
        return BOOKSTORE_FILE_LOADER.load(self.settings['jinja2_env'], name)


class BookstoreCloneAPIHandler(APIHandler):
    """Handle notebook clone from storage.

    Provides API handling for ``POST`` and clones a notebook
    from storage (S3).

    Methods
    -------
    initialize(self)
        Helper to access bookstore settings.
    post(self)
        Clone a notebook from the location specified by the payload.
    build_content_model(self, obj, path)
        Helper that takes a response from S3 and creates a ContentsAPI compatible model.
    build_post_response_model(self, model, obj, s3_bucket, s3_object_key)
        Helper that takes a Jupyter Contents API compliant model and adds cloning specific information.

    See also
    --------
    `Jupyter Notebook reference on Custom Handlers <https://jupyter-notebook.readthedocs.io/en/stable/extending/handlers.html#registering-custom-handlers>`_
    """

    def initialize(self):
        """Helper to retrieve bookstore setting for the session."""
        self.bookstore_settings = BookstoreSettings(config=self.config)

        self.session = aiobotocore.get_session()

    async def _clone(self, s3_bucket, s3_object_key):
        """Main function that handles communicating with S3 to initiate the clone.

        Parameters
        ----------
        s3_bucket: str
            Log (usually from the NotebookApp) for logging endpoint changes.
        s3_object_key: str
            The the path we wish to clone to.
        """

        self.log.info(f"bucket: {s3_bucket}")
        self.log.info(f"key: {s3_object_key}")

        async with self.session.create_client(
            's3',
            aws_secret_access_key=self.bookstore_settings.s3_secret_access_key,
            aws_access_key_id=self.bookstore_settings.s3_access_key_id,
            endpoint_url=self.bookstore_settings.s3_endpoint_url,
            region_name=self.bookstore_settings.s3_region_name,
        ) as client:
            self.log.info(f"Processing clone of {s3_object_key}")
            try:
                obj = await client.get_object(Bucket=s3_bucket, Key=s3_object_key)
                content = (await obj['Body'].read()).decode('utf-8')
            except ClientError as e:
                status_code = e.response['ResponseMetadata'].get('HTTPStatusCode')
                raise web.HTTPError(status_code, e.args[0])

            self.log.info(f"Obtained contents for {s3_object_key}")

        return obj, content

    @web.authenticated
    async def post(self):
        """POST /api/bookstore/clone

        Clone a notebook to the path specified in the payload.

        The payload type for the request should be::

            {
            "s3_bucket": string,
            "s3_key": string,
            "target_path"?: string
            }

        The response payload should match the standard Jupyter contents
        API POST response.
        """
        model = self.get_json_body()
        s3_bucket = model.get("s3_bucket", "")
        if s3_bucket == '' or s3_bucket == "/":
            raise web.HTTPError(400, "Must have a bucket to clone from")

        # s3_paths module has an s3_key function; s3_object_key avoids confusion
        s3_object_key = model.get("s3_key", "")
        if s3_object_key == '' or s3_object_key == '/':
            raise web.HTTPError(400, "Must have a key to clone from")

        target_path = model.get("target_path", "") or os.path.basename(
            os.path.relpath(s3_object_key)
        )

        self.log.info(f"About to clone from {s3_object_key}")
        obj, content = await self._clone(s3_bucket, s3_object_key)

        content_model = self.build_content_model(content, target_path)

        self.log.info(f"Completing clone for {s3_object_key}")
        self.contents_manager.save(content_model, content_model['path'])

        resp_model = self.build_post_response_model(content_model, obj, s3_bucket, s3_object_key)

        self.set_status(obj['ResponseMetadata']['HTTPStatusCode'])
        self.set_header('Content-Type', 'application/json')
        self.finish(resp_model)

    def build_content_model(self, content, target_path):
        """Helper that takes a response from S3 and creates a ContentsAPI compatible model.
        
        If the file at target_path already exists, this increments the file name.
        
        Parameters
        ----------
        content : str
            string encoded file content
        target_path : str
            The the path we wish to clone to, may be incremented if already present.

        Returns
        --------
        dict
            Jupyter Contents API compatible model
        """
        path = self.contents_manager.increment_filename(target_path)
        if os.path.splitext(path)[1] in [".ipynb", ".jpynb"]:
            model = build_notebook_model(content, path)
        else:
            model = build_file_model(content, path)
        return model

    def build_post_response_model(self, model, obj, s3_bucket, s3_object_key):
        """Helper that takes a Jupyter Contents API compliant model and adds cloning specific information.

        Parameters
        ----------
        model : dict
            Jupyter Contents API model
        obj : dict
            Log (usually from the NotebookApp) for logging endpoint changes.
        s3_bucket : str
            The S3 bucket we are cloning from
        s3_object_key: str
            The S3 key we are cloning

        Returns
        --------
        dict
            Model with additional info about the S3 cloning
        """
        model = deepcopy(model)
        model["s3_path"] = s3_display_path(s3_bucket, s3_object_key)
        if 'VersionId' in obj:
            model["versionID"] = obj['VersionId']
        return model
