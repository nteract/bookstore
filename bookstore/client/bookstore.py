import requests

from .notebook import CurrentNotebookClient


class BookstoreClient(CurrentNotebookClient):
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
