const path = require("path");
const fs = require("fs");

const _ = require("lodash");

const s3 = require("./s3");
const { JupyterServer } = require("./jupyter");

const { sleep } = require("./sleep");

// Keep the jupyter server around to make sure we can destroy on bad exit
let jupyterServer = null;

function cleanupJupyter() {
  if (jupyterServer && jupyterServer.process && !jupyterServer.process.killed) {
    console.log("cleaning up a rogue jupyter server");
    jupyterServer.process.kill();
  }
}

// Clean up on general close
process.on("exit", cleanupJupyter);

// Clean up on ctrl+c
process.on("SIGINT", cleanupJupyter);

// Clean up from `kill pid`, e.g. nodemon restart
process.on("SIGUSR1", cleanupJupyter);
process.on("SIGUSR2", cleanupJupyter);

// Clean up from uncaught exceptions
process.on("uncaughtException", cleanupJupyter);

// Catch all rogue promise rejections to ensure we fail CI
process.on("unhandledRejection", error => {
  cleanupJupyter();
  console.log("unhandledRejection", error);
  console.error(error.stack);
  process.exit(2);
});

console.log("running bookstore integration tests");

const main = async () => {
  const bucketName = "bookstore";

  jupyterServer = new JupyterServer();
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

  async function compareNotebooks(filepath, originalNotebook) {
    /***** Check notebook from S3 *****/
    const rawNotebook = await s3Client.getObject(
      bucketName,
      `ci-workspace/${filepath}`
    );

    console.log(filepath);
    console.log(rawNotebook);

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
      fs.readFile(path.join(__dirname, filepath), (err, data) => {
        if (err) {
          reject(err);
        } else {
          resolve(JSON.parse(data));
        }
      })
    );

    if (!_.isEqual(diskNotebook, originalNotebook)) {
      console.error("original");
      console.error(originalNotebook);
      console.error("from disk");
      console.error(diskNotebook);
      throw new Error("Notebook on Disk does not match what we sent");
    }
  }

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

  await jupyterServer.writeNotebook(
    "ci-local-writeout.ipynb",
    originalNotebook
  );

  const basicNotebook = {
    cells: [],
    nbformat: 4,
    nbformat_minor: 2,
    metadata: {
      save: 1
    }
  };

  for (var ii = 0; ii < 4; ii++) {
    await jupyterServer.writeNotebook("ci-local-writeout2.ipynb", {
      cells: [],
      nbformat: 4,
      nbformat_minor: 2,
      metadata: {
        save: ii
      }
    });
    await jupyterServer.writeNotebook("ci-local-writeout3.ipynb", {
      cells: [{ cell_type: "markdown", source: "# Hello world", metadata: {} }],
      nbformat: 4,
      nbformat_minor: 2,
      metadata: {}
    });
  }

  // Wait for minio to have the notebook
  // Future iterations of this script should poll to get the notebook
  await sleep(1000);

  jupyterServer.shutdown();

  await compareNotebooks("ci-local-writeout.ipynb", originalNotebook);
  await compareNotebooks("ci-local-writeout2.ipynb", {
    cells: [],
    nbformat: 4,
    nbformat_minor: 2,
    metadata: {
      save: 3
    }
  });

  console.log("📚 Bookstore Integration Complete 📚");
};

main();
