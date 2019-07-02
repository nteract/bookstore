"""Client to interact with a notebook's bookstore functionality."""
import requests

from .nb_client import CurrentNotebookClient


class BookstoreClient(CurrentNotebookClient):
    """EXPERIMENTAL SUPPORT: A client that allows access to a Bookstore from within a notebook.
    
    Parameters
    ----------
    s3_bucket: str
        (optional) Provide a default bucket for this bookstore client to clone from.
    

    Attributes
    ----------
    default_bucket : str
        The default bucket to be used for cloning.
    """

    def __init__(self, s3_bucket=None):
        if s3_bucket:
            self.default_bucket = s3_bucket
        super().__init__()

    @property
    def publish_endpoint(self):
        """Helper to refer to construct the publish endpoint for this notebook server."""
        api_endpoint = "/api/bookstore/publish/"
        return f"{self.url}{api_endpoint}"

    def publish(self, path=None):
        """Publish notebook to bookstore
        
        Parameters
        ----------
        path : str
            (optional) Path that you wish to publish; defaults to current notebook.
        s3_object_key: str
            The the path we wish to clone to.
        """
        if path is None:
            path = self.session.path
        nb_json = self.get_contents(path)['content']
        json_body = {"type": "notebook", "content": nb_json}

        target_url = f"{self.publish_endpoint}{path}"

        response = self.req_session.put(target_url, json=json_body)
        return response

    @property
    def clone_endpoint(self):
        """Helper to refer to construct the clone endpoint for this notebook server."""
        api_endpoint = "/api/bookstore/clone/"
        return f"{self.url}{api_endpoint}"

    def clone(self, s3_bucket="", s3_key="", target_path=""):
        """Clone files via bookstore.
        
        Parameters
        ----------
        s3_bucket : str
            (optional) S3 bucket you wish to clone from; defaults to client's bucket.
        s3_object_key: str
            The object key describing the object you wish to clone from S3.
        target_path: str
            (optional) The location you wish to clone the object to; defaults to s3_object_key.
        """
        s3_bucket = s3_bucket or self.default_bucket
        json_body = {"s3_bucket": s3_bucket, "s3_key": s3_key, "target_path": target_path}
        # TODO: Add a check for success
        response = self.req_session.post(f"{self.clone_endpoint}", json=json_body)
        return response
