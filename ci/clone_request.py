""" Helper for interactive debug of cloning endpoint.

This module is intended to be used to interactively when debugging the
bookstore cloning endpoint.

To use and test this, you'll need to separately run a Jupyter server.

Example Usage
-------------

To test the 'nteract-notebooks' bucket on S3 you'll need to run a command like
the following::

jupyter notebook --NotebookApp.allow_origin="*" --NotebookApp.disable_check_xsrf=True \
    --no-browser --NotebookApp.token="" \
    --BookstoreSettings.s3_bucket=nteract-notebooks

To test the 'bookstore' bucket created with minio you'll need to run a command
like the following::

jupyter notebook --NotebookApp.allow_origin="*" --NotebookApp.disable_check_xsrf=True \
    --no-browser --NotebookApp.token="" \
    --BookstoreSettings.s3_endpoint_url="http://localhost:9000" \
    --BookstoreSettings.s3_access_key_id="ONLY_ON_CIRCLE" \
    --BookstoreSettings.s3_secret_access_key="CAN_WE_DO_THIS"

Additional examples
-------------------

See the docstring under the ``if __name__`` statement below.
"""
import nbformat
import pprint
import requests


def get(queries):
    return requests.get(f"http://localhost:8888/api/bookstore/cloned{queries}")


def post(**kwargs):
    return requests.post("http://localhost:8888/api/bookstore/cloned", json={**kwargs})


if __name__ == "__main__":
    """
    Examples
    --------

    # tests s3 hosted 'nteract-notebooks' bucket
    response = get("?s3_bucket=nteract-notebooks&s3_key=published/whateverwewant.json")
    print(response.content)
    response = get("/?s3_bucket=nteract-notebooks&s3_key=published/whateverwewant.json")
    print(response.content)
    response = get("?s3_bucket=nteract-notebooks&s3_key=Introduction_to_Chainer.ipynb")
    print(response.content)


    # tests minio created 'bookstore' bucket
    response = get("?s3_bucket=bookstore&s3_key=ci-published/ci-published.ipynb")
    print(response.content)
    response = post(s3_bucket="nteract-notebooks", s3_key="Introduction_to_Chainer.ipynb")
    print(response.content)

    Changing the requests will enable you to test different situations and
    analyze the responses.
    """
    response = post(s3_bucket="bookstore", s3_key="ci-published/ci-published.ipynb")
    pprint.pprint(response.json())
    response = post(
        s3_bucket="bookstore",
        s3_key="ci-published/ci-published.ipynb",
        target_path="published/this_is_my_target_path.ipynb",
    )
    pprint.pprint(response.json())
