import requests

from .notebook import CurrentNotebookClient


class BookstoreClient(CurrentNotebookClient):
    def __init__(self, s3_bucket=""):
        if s3_bucket:
            self.default_bucket = s3_bucket
        super().__init__()

    @property
    def publish_endpoint(self):
        api_endpoint = "/api/bookstore/published/"
        return f"{self.url}{api_endpoint}"

    def publish(self):
        nb_json = self.get_contents(self.notebook['path'])['content']
        req = {
            "json": {"type": "notebook", "content": nb_json},
            "headers": {"Content-Type": "application/json", 'Authorization': f'token {self.token}'},
        }

        target_url = f"{self.publish_endpoint}{self.notebook['path']}"

        resp = requests.put(target_url, **req)
        return resp

    @property
    def clone_endpoint(self):
        api_endpoint = "/api/bookstore/cloned/"
        return f"{self.url}{api_endpoint}"

    def clone(self, s3_bucket="", s3_key="", target_path=""):
        s3_bucket = s3_bucket or self.default_bucket
        req_dict = {"s3_bucket": s3_bucket, "s3_key": s3_key, "target_path": target_path}
        req = {
            "json": req_dict,
            "headers": {"Content-Type": "application/json", 'Authorization': f'token {self.token}'},
        }

        target_url = f"{self.clone_endpoint}"
        resp = requests.post(target_url, **req)
        return resp

