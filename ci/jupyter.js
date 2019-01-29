const child_process = require("child_process");
const { genToken } = require("./token");
const { sleep } = require("./sleep");

// "Polyfill" XMLHttpRequest for rxjs' ajax to use
global.XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
const { ajax } = require("rxjs/ajax");

class JupyterServer {
  constructor(config = {}) {
    this.port = config.port || 9988;
    this.ip = config.ip || "127.0.0.1";
    this.scheme = config.scheme || "http";
    this.token = null;

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
        `--port=${this.port}`,
        `--ip=${this.ip}`
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
    const xhr = await ajax({
      url: `${this.endpoint}/api/contents/${path}`,
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
    const xhr = await ajax({
      url: `${this.endpoint}/api/bookstore/published/${path}`,
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

  shutdown() {
    this.process.kill();
  }

  get endpoint() {
    return `${this.scheme}://${this.ip}:${this.port}`;
  }
}

module.exports = {
  JupyterServer
};
