const child_process = require("child_process");
const path = require("path");
const fs = require("fs");

const _ = require("lodash");

const s3 = require("./s3");
const { JupyterServer } = require("./jupyter");
const { url_path_join } = require("./utils");

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

  async function compareS3Notebooks(filepath, originalNotebook) {
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

  async function comparePublishedNotebooks(filepath, originalNotebook) {
    /***** Check published notebook from S3 prefix *****/
    const rawNotebook = await s3Client.getObject(
      bucketName,
      `ci-published/${filepath}`
    );

    console.log(filepath);
    console.log(rawNotebook);

    const notebook = JSON.parse(rawNotebook);
    console.log("Checking whether Notebook on s3 matches what we sent.");

    if (!_.isEqual(notebook, originalNotebook)) {
      console.error("original");
      console.error(originalNotebook);
      console.error("from s3");
      console.error(notebook);
      throw new Error("Notebook on S3 does not match what we sent");
    }

    console.log("Notebook on S3 matches what we sent");
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

  const EmptyNotebook = {
    cells: [
      {
        cell_type: "code",
        execution_count: null,
        metadata: {},
        outputs: [],
        source: []
      }
    ],
    metadata: {
      kernelspec: {
        display_name: "dev",
        language: "python",
        name: "dev"
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
        version: "3.6.8"
      }
    },
    nbformat: 4,
    nbformat_minor: 2
  };

  await jupyterServer.writeNotebook(
    "ci-local-writeout.ipynb",
    originalNotebook
  );

  await jupyterServer.publishNotebook("ci-published.ipynb", originalNotebook);

  await comparePublishedNotebooks("ci-published.ipynb", originalNotebook);

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
    await sleep(100);
  }

  function s3CloneLandingQueryCheck(s3Key, expectedQueryString) {
    const populatedQueryString = jupyterServer.populateS3CloneLandingQuery(
      bucketName,
      s3Key
    );
    if (!_.isEqual(populatedQueryString, expectedQueryString)) {
      console.error("created");
      console.error(populatedQueryString);
      console.error("expected");
      console.error(expectedQueryString);
      throw new Error("Query was not formed properly");
    }
    console.log(`Query matched ${expectedQueryString}`);
  }

  function checkS3CloneLandingResponse(res, expected) {
    const content = res.response;
    if (!content.includes(expected)) {
      console.error("Response is ill-formed:");
      console.error(content);
      console.error("It is expected to contain:");
      console.error(expected);
      throw new Error("Ill-formed response.");
    }
    console.log(`Clone endpoint for ${expected} reached successfully!`);
  }

  const publishedPath = "ci-published/ci-published.ipynb";
  s3CloneLandingQueryCheck(
    publishedPath,
    url_path_join(
      jupyterServer.endpoint,
      `bookstore/clone?s3_bucket=${bucketName}&s3_key=${publishedPath}`
    )
  );
  const s3CloneLandingRes = await jupyterServer.cloneS3NotebookLanding(
    bucketName,
    publishedPath
  );
  checkS3CloneLandingResponse(s3CloneLandingRes, publishedPath);

  await jupyterServer.cloneS3Notebook(bucketName, publishedPath);
  await jupyterServer.cloneFSNotebook("test_files/EmptyNotebook.ipynb");
  // Wait for minio to have the notebook
  // Future iterations of this script should poll to get the notebook
  await sleep(2000);

  await compareS3Notebooks("ci-published.ipynb", originalNotebook);
  await compareS3Notebooks("ci-local-writeout.ipynb", originalNotebook);
  await compareS3Notebooks("ci-local-writeout2.ipynb", {
    cells: [],
    nbformat: 4,
    nbformat_minor: 2,
    metadata: {
      save: 3
    }
  });
  await compareS3Notebooks("EmptyNotebook.ipynb", EmptyNotebook);

  await sleep(700);

  await jupyterServer.deleteNotebook("ci-published.ipynb");
  await jupyterServer.deleteNotebook("ci-local-writeout.ipynb");
  await jupyterServer.deleteNotebook("ci-local-writeout2.ipynb");
  await jupyterServer.deleteNotebook("ci-local-writeout3.ipynb");
  await jupyterServer.deleteNotebook("EmptyNotebook.ipynb");

  jupyterServer.shutdown();

  console.log("📚 Bookstore Integration Complete 📚");
};

main();
