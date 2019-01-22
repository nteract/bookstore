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

In one session run `ci/local.sh`, this will start up minio.

In the other session run `node ci/integration.js`, this will run the integration tests
