const child_process = require("child_process");
const { randomBytes } = require("crypto");
const path = require("path");
const fs = require("fs");

global.XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;

const { ajax } = require("rxjs/ajax");

const rxJupyter = require("rx-jupyter");

const _ = require("lodash");

console.log("running bookstore integration tests");

async function genToken(byteLength = 32) {
  return new Promise((resolve, reject) => {
    randomBytes(byteLength, (err, buffer) => {
      if (err) {
        reject(err);
        return;
      }

      resolve(buffer.toString("hex"));
    });
  });
}

const sleep = timeout =>
  new Promise((resolve, reject) => setTimeout(resolve, timeout));

// Catch all rogue promise rejections to fail CI
process.on("unhandledRejection", error => {
  console.log("unhandledRejection", error.message);
  process.exit(2);
});

var Minio = require("minio");

const main = async () => {
  const jupyterToken = await genToken();
  const jupyterPort = 9988;
  const jupyterEndpoint = `http://127.0.0.1:${jupyterPort}`;

  const bucketName = "bookstore";
  // Optional according to minio docs, likely here for AWS compat
  const regionName = "us-east-1";

  const s3Config = {
    endPoint: "127.0.0.1",
    port: 9000,
    useSSL: false,
    accessKey: "ONLY_ON_CIRCLE",
    secretKey: "CAN_WE_DO_THIS"
  };

  // Instantiate the minio client with the endpoint
  // and access keys as shown below.
  var minioClient = new Minio.Client(s3Config);

  const madeBucket = await new Promise((resolve, reject) => {
    minioClient.makeBucket(bucketName, regionName, err => {
      if (err) {
        reject(err);
        return;
      }
      resolve();
    });
  });
  console.log(`Created bucket ${bucketName}`);

  const jupyter = child_process.spawn(
    "jupyter",
    [
      "notebook",
      "--no-browser",
      `--NotebookApp.token=${jupyterToken}`,
      `--NotebookApp.disable_check_xsrf=True`,
      `--port=${jupyterPort}`,
      `--ip=127.0.0.1`
    ],
    { cwd: __dirname }
  );

  ////// Refactor me later, streams are a bit messy with async await
  // Check to see that jupyter is up
  let jupyterUp = false;

  jupyter.stdout.on("data", data => {
    const s = data.toString();
    console.log(s);
  });
  jupyter.stderr.on("data", data => {
    const s = data.toString();

    console.error(s);
    if (s.includes("Jupyter Notebook is running at")) {
      jupyterUp = true;
    }
  });
  jupyter.stdout.on("end", data => console.log("DONE WITH JUPYTER"));

  jupyter.on("exit", code => {
    if (code != 0) {
      // Jupyter exited badly
      console.error("jupyter errored", code);
      process.exit(code);
    }
  });

  await sleep(3000);

  if (!jupyterUp) {
    console.log("jupyter has not come up after 3 seconds, waiting 3 more");
    await sleep(3000);

    if (!jupyterUp) {
      console.log("jupyter has not come up after 6 seconds, bailing");
      process.exit(1);
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

  const xhr = await ajax({
    url: `${jupyterEndpoint}/api/contents/ci-local-writeout.ipynb`,
    responseType: "json",
    createXHR: () => new XMLHttpRequest(),
    method: "PUT",
    body: {
      type: "notebook",
      content: originalNotebook
    },
    headers: {
      "Content-Type": "application/json",
      Authorization: `token ${jupyterToken}`
    }
  }).toPromise();

  // Wait for minio to have the notebook
  // Future iterations of this script should poll to get the notebook
  await sleep(1000);

  jupyter.kill();

  //// Check the notebook we placed on S3
  const rawNotebook = await new Promise((resolve, reject) =>
    minioClient.getObject(
      bucketName,
      "ci-workspace/ci-local-writeout.ipynb",
      (err, dataStream) => {
        if (err) {
          console.error("wat");
          reject(err);
          return;
        }

        const chunks = [];
        dataStream.on("data", chunk => chunks.push(chunk));
        dataStream.on("error", reject);
        dataStream.on("end", () => {
          resolve(Buffer.concat(chunks).toString("utf8"));
        });
      }
    )
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

  //// Check the notebook we placed on Disk
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
