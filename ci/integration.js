const path = require("path");
const fs = require("fs");

const _ = require("lodash");

const s3 = require("./s3");
const { JupyterServer } = require("./jupyter");

const { sleep } = require("./sleep");

// Catch all rogue promise rejections to fail CI
process.on("unhandledRejection", error => {
  console.log("unhandledRejection", error.message);
  console.error(error.stack);
  process.exit(2);
});

console.log("running bookstore integration tests");

const main = async () => {
  const bucketName = "bookstore";

  const jupyterServer = new JupyterServer();
  await jupyterServer.start();

  const s3Config = {
    endPoint: "127.0.0.1",
    port: 9000,
    useSSL: false,
    accessKey: "ONLY_ON_CIRCLE",
    secretKey: "CAN_WE_DO_THIS"
  };

  // Instantiate the minio client with the endpoint
  // and access keys as shown below.
  var s3Client = new s3.Client(s3Config);

  await s3Client.makeBucket(bucketName);

  console.log(`Created bucket ${bucketName}`);

  const originalNotebook = {
    cells: [
      {
        cell_type: "code",
        execution_count: null,
        metadata: {},
        outputs: [],
        source: ["import this"]
      }
    ],
    metadata: {
      kernelspec: {
        display_name: "Python 3",
        language: "python",
        name: "python3"
      },
      language_info: {
        codemirror_mode: {
          name: "ipython",
          version: 3
        },
        file_extension: ".py",
        mimetype: "text/x-python",
        name: "python",
        nbconvert_exporter: "python",
        pygments_lexer: "ipython3",
        version: "3.7.0"
      }
    },
    nbformat: 4,
    nbformat_minor: 2
  };

  jupyterServer.writeNotebook("ci-local-writeout.ipynb", originalNotebook);

  // Wait for minio to have the notebook
  // Future iterations of this script should poll to get the notebook
  await sleep(1000);

  jupyterServer.shutdown();

  /***** Check notebook from S3 *****/
  const rawNotebook = await s3Client.getObject(
    bucketName,
    "ci-workspace/ci-local-writeout.ipynb"
  );

  const notebook = JSON.parse(rawNotebook);

  if (!_.isEqual(notebook, originalNotebook)) {
    console.error("original");
    console.error(originalNotebook);
    console.error("from s3");
    console.error(notebook);
    throw new Error("Notebook on S3 does not match what we sent");
  }

  console.log("Notebook on S3 matches what we sent");

  /***** Check notebook from Disk *****/
  const diskNotebook = await new Promise((resolve, reject) =>
    fs.readFile(
      path.join(__dirname, "ci-local-writeout.ipynb"),
      (err, data) => {
        if (err) {
          reject(err);
        } else {
          resolve(JSON.parse(data));
        }
      }
    )
  );

  if (!_.isEqual(diskNotebook, originalNotebook)) {
    console.error("original");
    console.error(originalNotebook);
    console.error("from disk");
    console.error(diskNotebook);
    throw new Error("Notebook on Disk does not match what we sent");
  }

  console.log("📚 Bookstore Integration Complete 📚");
};

main();
