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

2. In one terminal run `ci/local.sh`. This will start up minio.

3. In the other terminal run `node ci/integration.js`. This will run the
   integration tests
