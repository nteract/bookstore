// Optional according to minio docs, included for AWS compat
const regionName = "us-east-1";

const Minio = require("minio");

function makeBucket(minioClient, bucketName) {
  return new Promise((resolve, reject) => {
    minioClient.makeBucket(bucketName, regionName, err => {
      if (err) {
        // When using the ci script locally, the bucket typically already exists
        if (err.code === "BucketAlreadyOwnedByYou") {
          console.warn("Bucket already created");
          resolve();
          return;
        }

        reject(err);
        return;
      }
      resolve();
    });
  });
}

function getObject(minioClient, bucketName, objectName) {
  return new Promise((resolve, reject) =>
    minioClient.getObject(bucketName, objectName, (err, dataStream) => {
      if (err) {
        reject(err);
        return;
      }

      const chunks = [];
      dataStream.on("data", chunk => chunks.push(chunk));
      dataStream.on("error", reject);
      dataStream.on("end", () => {
        resolve(Buffer.concat(chunks).toString("utf8"));
      });
    })
  );
}

class Client {
  constructor(s3Config) {
    this.minioClient = new Minio.Client(s3Config);
  }

  makeBucket(bucketName) {
    return makeBucket(this.minioClient, bucketName);
  }

  getObject(bucketName, objectName) {
    return getObject(this.minioClient, bucketName, objectName);
  }
}

module.exports = {
  Client
};
