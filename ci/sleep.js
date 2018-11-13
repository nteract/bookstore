module.exports = {
  sleep: timeout =>
    new Promise((resolve, reject) => setTimeout(resolve, timeout))
};
