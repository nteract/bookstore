const { randomBytes } = require("crypto");

function genToken(byteLength = 32) {
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

module.exports = {
  genToken
};
