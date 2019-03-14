# Local Continuous Integration 

It helps when developing to be able to run integration tests. Because bookstore relies on 
accessing s3 this requires that we create a local server that can model how s3 works.

We will be using [minio](https://docs.minio.io/) to serve these responses.

## Setup Local CI 

In order to run the ci tests locally you will need to have a few things set up.

You will need to have a functioning `docker`. 

Additionally, you will need to have `/mnt/data/` and `/mnt/config/` defined and given full permissions (e.g., with `chmod 777 /mnt/data`).

You will then need to add `/mnt/data` and `/mnt/config` to be accessible from docker.
You can do so by modifying Docker's preferences by going to Docker → Preferences → File Sharing 
and adding `/mnt/data` and `/mnt/config` to the list there.

You will also need a up-to-date version of `node`.

## Run Local tests

Create two shell sessions with working directories as the `bookstore` directory. 

In one session run `yarn test:server` (this will start up minio).

In the other session run `yarn test`, this will run the integration tests.

## Interactive python tests

The CI scripts are designed to be self-contained and run in an automated setup. This makes it
makes it harder to iterate rapidly when you don't want to test the _entire_ system but when
you do need to integrate with a Jupyter server.

In addition the CI scripts, we have included `./ci/clone_request.py` for testing the clone
endpoint. This is particularly useful for the `/api/bookstore/clone` endpoint because while it
is an API to be used by other applications, it also acts as a user facing endpoint since it
provides a landing page for confirming whether or not a clone is to be approved.

It's often difficult to judge whether what is being served makes sense from a UI perspective
without being able to investigate it directly. At the same time we'll need to access it as an
API to ensure that the responses are well-behaved from an API standpoint. By using python to
query a live server and a browser to visit the landing page, we can rapidly iterate between
the API and UI contexts from the same live server's endpoint. 

We provide examples of `jupyter notebook` commands needed in that file as well for both
accessing the `nteract-notebooks` S3 bucket as well as the Minio provided `bookstore` bucket
(as used by the CI scripts).
