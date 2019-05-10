# Local Continuous Integration

It helps when developing to be able to run integration tests locally. Since
bookstore relies on accessing S3, this requires that we create a local server
that can model how S3 works.

We will be using [minio](https://docs.minio.io/) to mock S3 behavior.

## Setup Local CI environment

To run the ci tests locally, you will need to have a few things set up:

- a functioning `docker` service
- define `/mnt/data/` and `/mnt/config/` and give full permissions
  (e.g., `chmod 777 /mnt/data`).
= add `/mnt/data` and `/mnt/config` to be accessible from `docker`. You can do
  so by modifying Docker's preferences by going to `Docker → Preferences → File Sharing`
  and adding `/mnt/data` and `/mnt/config` to the list there.
- an up-to-date version of `node`.

## Run Local tests

1. Open two terminals with the current working directory as the root `bookstore`
   directory.

2. In one terminal run `yarn test:server`. This will start up minio.

3. In the other terminal run `yarn test`. This will run the integration tests.

## Interactive python tests

The CI scripts are designed to be self-contained and run in an automated setup. This makes it
makes it harder to iterate rapidly when you don't want to test the _entire_ system but when
you do need to integrate with a Jupyter server.

In addition the CI scripts, we have included `./ci/clone_request.py` for testing the clone
endpoint. This is particularly useful for the `/api/bookstore/cloned` endpoint because while it
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
