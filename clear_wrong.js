/*
 * JS code to clear wrong question list
 *
 * Paste the following code in web console.
 */

QUOTED_RE = new RegExp("'[^']+'");
getparam = s => {
  s = QUOTED_RE.exec(s)[0];
  return s.slice(1, s.length - 1);
};
document.querySelectorAll("button.btn").forEach(node => {
  clickfndesc = node.getAttribute("onclick");
  if (clickfndesc) {
    qid = getparam(clickfndesc);
    $.post("http://tk.ipmph.com/exam/a/exam/questionWrong/deleteOne", {
      prop5: "del",
      id: qid
    });
  }
});
