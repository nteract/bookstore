import requests
import nbformat
import pprint

'''
This is intended to be used to interactively debug the bookstore cloning endpoint.

If you want to test this, you'll need to separately run a Jupyter server. 

Depending on what you want to test you'll need to run different commands

To test the 'nteract-notebooks' bucket on S3 you'll need to run a command like the following
jupyter notebook --NotebookApp.allow_origin="*" --NotebookApp.disable_check_xsrf=True \
    --no-browser --NotebookApp.token="" \ 
    --BookstoreSettings.s3_bucket=nteract-notebooks 

To test the 'bookstore' bucket created with minio you'll need to run a command like the following
jupyter notebook --NotebookApp.allow_origin="*" --NotebookApp.disable_check_xsrf=True \
    --no-browser --NotebookApp.token="" \
    --BookstoreSettings.s3_endpoint_url="http://localhost:9000" \
    --BookstoreSettings.s3_access_key_id="ONLY_ON_CIRCLE" \
    --BookstoreSettings.s3_secret_access_key="CAN_WE_DO_THIS"
'''


def get(queries):
    return requests.get(f"http://localhost:8888/api/bookstore/cloned{queries}")


def post(**kwargs):
    return requests.post("http://localhost:8888/api/bookstore/cloned", json={**kwargs})


if __name__ == "__main__":

    # tests s3 hosted 'nteract-notebooks' bucket
    # res = get("?s3_bucket=nteract-notebooks&s3_key=published/whateverwewant.json")
    # print(res.content)
    # res = get("/?s3_bucket=nteract-notebooks&s3_key=published/whateverwewant.json")
    # print(res.content)
    # res = get("?s3_bucket=nteract-notebooks&s3_key=Introduction_to_Chainer.ipynb")
    # print(res.content)

    # tests minio created 'bookstore' bucket
    # res = get("?s3_bucket=bookstore&s3_key=ci-published/ci-published.ipynb")
    # print(res.content)
    # res = post(s3_bucket="nteract-notebooks", s3_key="Introduction_to_Chainer.ipynb")
    # print(res.content)
    res = post(s3_bucket="bookstore", s3_key="ci-published/ci-published.ipynb")
    pprint.pprint(res.json())
    res = post(
        s3_bucket="bookstore",
        s3_key="ci-published/ci-published.ipynb",
        target_path="published/this_is_my_target_path.ipynb",
    )
    pprint.pprint(res.json())
