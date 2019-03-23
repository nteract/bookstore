import requests

from .notebook import CurrentNotebookClient


class BookstoreClient(CurrentNotebookClient):
    """Represents a bookstore client that corresponds to the active nb client"""

    def __init__(self, s3_bucket=""):
        if s3_bucket:
            self.default_bucket = s3_bucket
        super().__init__()

    @property
    def publish_endpoint(self):
        api_endpoint = "/api/bookstore/published/"
        return f"{self.url}{api_endpoint}"

    def publish(self, path=None):
        if path is None:
            path = self.session.path
        nb_json = self.get_contents(self.session.path)['content']
        json_body = {"type": "notebook", "content": nb_json}

        target_url = f"{self.publish_endpoint}{self.session.path}"

        resp = self.req_session.put(target_url, json=json_body)
        return resp

    @property
    def clone_endpoint(self):
        api_endpoint = "/api/bookstore/cloned/"
        return f"{self.url}{api_endpoint}"

    def clone(self, s3_bucket="", s3_key="", target_path=""):
        s3_bucket = s3_bucket or self.default_bucket
        json_body = {"s3_bucket": s3_bucket, "s3_key": s3_key, "target_path": target_path}
        target_url = f"{self.clone_endpoint}"
        # TODO: Add a check for success
        resp = self.req_session.post(target_url, json=json_body)
        return resp

