"""Client to interact with the notebook store"""
import requests

from .nb_client import CurrentNotebookClient


class BookstoreClient(CurrentNotebookClient):
    """Represents a bookstore client that corresponds to the active nb client"""

    def __init__(self, s3_bucket=None):
        if s3_bucket:
            self.default_bucket = s3_bucket
        super().__init__()

    @property
    def publish_endpoint(self):
        api_endpoint = "/api/bookstore/publish/"
        return f"{self.url}{api_endpoint}"

    def publish(self, path=None):
        """Publish notebook to bookstore"""
        if path is None:
            path = self.session.path
        nb_json = self.get_contents(path)['content']
        json_body = {"type": "notebook", "content": nb_json}

        target_url = f"{self.publish_endpoint}{path}"

        response = self.req_session.put(target_url, json=json_body)
        return response

    @property
    def clone_endpoint(self):
        api_endpoint = "/api/bookstore/clone/"
        return f"{self.url}{api_endpoint}"

    def clone(self, s3_bucket="", s3_key="", target_path=""):
        s3_bucket = s3_bucket or self.default_bucket
        json_body = {"s3_bucket": s3_bucket, "s3_key": s3_key, "target_path": target_path}
        # TODO: Add a check for success
        response = self.req_session.post(f"{self.clone_endpoint}", json=json_body)
        return response
