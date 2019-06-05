const url_path_join = function (...pieces) {
  // """Join components of url into a relative url
  // Use to prevent double slash when joining subpaths.
  // This will leave the initial and final / in place
  //
  // url_path_join("http://127.0.0.1:9988", "mybaseUrl/ipynb", "/api/contents//") => "http://127.0.0.1:9988/mybaseUrl/ipynb/api/contents/"
  //
  // They will be readded in between words, and at the beginning and end if they were
  // """
  const initial = pieces[0].startsWith("/");
  const final = pieces[pieces.length - 1].endsWith("/");
  let result = pieces
    .filter(el => el !== "")
    .map(el => el.replace(/(^[ /]+)|([/]+$)/g, ""))
    .join("/");
  if (initial) {
    result = "/" + result;
  }
  if (final) {
    result = result + "/";
  }
  if (result == "//") {
    result = "/";
  }
  return result;
};

module.exports = {
  url_path_join
};
