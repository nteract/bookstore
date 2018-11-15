#!/bin/bash
set -euo pipefail
IFS=$'\n\t'


# Run a minio server locally in a similar manner to how we do on CI

docker rm -f minio-like-ci || true # Plow forward regardless
docker run -p 9000:9000 \
       --name minio-like-ci \
       -e MINIO_ACCESS_KEY=ONLY_ON_CIRCLE \
       -e MINIO_SECRET_KEY=CAN_WE_DO_THIS \
       -v /mnt/data:/data -v /mnt/config:/Users/kylek/.minio \
       minio/minio server /data
