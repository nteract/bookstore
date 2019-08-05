const child_process = require("child_process");
const { genToken } = require("./token");
const { sleep } = require("./sleep");
const { url_path_join } = require("./utils");

// "Polyfill" XMLHttpRequest for rxjs' ajax to use
global.XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
const { ajax } = require("rxjs/ajax");

class JupyterServer {
  constructor(config = {}) {
    this.port = config.port || 9988;
    this.ip = config.ip || "127.0.0.1";
    this.scheme = config.scheme || "http";
    this.token = null;
    this.baseUrl = config.baseUrl || "mybaseUrl/ipynb/";

    // Launch the server from the directory of this script by default
    this.cwd = config.cwd || __dirname;

    this.process = null;
    this.up = false;
  }

  async start() {
    if (!this.token) {
      this.token = await genToken();
    }

    // Kill off any prexisting process before creating a new one
    if (this.process) {
      this.process.kill();
    }

    this.process = child_process.spawn(
      "jupyter",
      [
        "notebook",
        "--no-browser",
        `--NotebookApp.token=${this.token}`,
        `--NotebookApp.disable_check_xsrf=True`,
        `--NotebookApp.base_url=${this.baseUrl}`,
        `--port=${this.port}`,
        `--ip=${this.ip}`,
        `--log-level=10`
      ],
      { cwd: this.cwd }
    );

    ////// Refactor me later, streams are a bit messy with async await
    ////// Let's use spawn-rx in the future and make some clean rxjs with timeouts
    this.process.stdout.on("data", data => {
      const s = data.toString();
      process.stdout.write(s);
    });
    this.process.stderr.on("data", data => {
      const s = data.toString();
      process.stderr.write(s);

      if (s.includes("Jupyter Notebook is running at")) {
        this.up = true;
      }
    });
    this.process.stdout.on("end", data =>
      console.log("jupyter server terminated")
    );

    await sleep(3000);

    if (!this.up) {
      console.log("jupyter has not come up after 3 seconds, waiting 3 more");
      await sleep(3000);

      if (!this.up) {
        throw new Error("jupyter has not come up after 6 seconds, bailing");
      }
    }
  }

  async writeNotebook(path, notebook) {
    // Once https://github.com/nteract/nteract/pull/3651 is merged, we can use
    // rx-jupyter for writing a notebook to the contents API
    const apiPath = "/api/contents/";
    const xhr = await ajax({
      url: url_path_join(this.endpoint, apiPath, path),
      responseType: "json",
      createXHR: () => new XMLHttpRequest(),
      method: "PUT",
      body: {
        type: "notebook",
        content: notebook
      },
      headers: {
        "Content-Type": "application/json",
        Authorization: `token ${this.token}`
      }
    }).toPromise();

    return xhr;
  }

  async publishNotebook(path, notebook) {
    // Once https://github.com/nteract/nteract/pull/3651 is merged, we can use
    // rx-jupyter for writing a notebook to the contents API
    const apiPath = "/api/bookstore/publish/";
    const xhr = await ajax({
      url: url_path_join(this.endpoint, apiPath, path),
      responseType: "json",
      createXHR: () => new XMLHttpRequest(),
      method: "PUT",
      body: {
        type: "notebook",
        content: notebook
      },
      headers: {
        "Content-Type": "application/json",
        Authorization: `token ${this.token}`
      }
    }).toPromise();

    return xhr;
  }

  populateS3CloneLandingQuery(s3Bucket, s3Key) {
    return url_path_join(
      this.endpoint,
      `/bookstore/clone?s3_bucket=${s3Bucket}&s3_key=${s3Key}`
    );
  }
  populateS3CloneQuery() {
    return url_path_join(this.endpoint, `/api/bookstore/clone`);
  }
  async cloneS3NotebookLanding(s3Bucket, s3Key) {
    // Once https://github.com/nteract/nteract/pull/3651 is merged, we can use
    // rx-jupyter for writing a notebook to the contents API
    const xhr = await ajax({
      url: this.populateS3CloneLandingQuery(s3Bucket, s3Key),
      responseType: "text",
      createXHR: () => new XMLHttpRequest(),
      method: "GET",
      headers: {
        Authorization: `token ${this.token}`
      }
    }).toPromise();

    return xhr;
  }
  async cloneS3Notebook(s3Bucket, s3Key) {
    const query = {
      url: this.populateS3CloneQuery(),
      responseType: "json",
      createXHR: () => new XMLHttpRequest(),
      body: { s3_bucket: s3Bucket, s3_key: s3Key },
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `token ${this.token}`
      }
    };
    const xhr = await ajax(query).toPromise();

    return xhr;
  }
  populateFSCloneLandingQuery(relpath) {
    return url_path_join(
      this.endpoint,
      `/bookstore/fs-clone?relpath=${relpath}`
    );
  }
  populateFSCloneQuery() {
    return url_path_join(this.endpoint, `/api/bookstore/fs-clone`);
  }
  async cloneFSNotebookLanding(relpath) {
    const xhr = await ajax({
      url: this.populateFSCloneLandingQuery(relpath),
      responseType: "text",
      createXHR: () => new XMLHttpRequest(),
      method: "GET",
      headers: {
        Authorization: `token ${this.token}`
      }
    }).toPromise();

    return xhr;
  }
  async cloneFSNotebook(relpath) {
    const query = {
      url: this.populateFSCloneQuery(),
      responseType: "json",
      createXHR: () => new XMLHttpRequest(),
      body: { relpath },
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `token ${this.token}`
      }
    };
    const xhr = await ajax(query).toPromise();

    return xhr;
  }

  async deleteNotebook(path) {
    const apiPath = "/api/contents/";
    const xhr = await ajax({
      url: url_path_join(this.endpoint, apiPath, path),
      responseType: "json",
      createXHR: () => new XMLHttpRequest(),
      method: "DELETE",
      headers: {
        Authorization: `token ${this.token}`
      }
    }).toPromise();

    return xhr;
  }
  shutdown() {
    this.process.kill();
  }

  get endpoint() {
    return url_path_join(
      `${this.scheme}://${this.ip}:${this.port}`,
      this.baseUrl
    );
  }
}

module.exports = {
  JupyterServer
};
