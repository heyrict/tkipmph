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
document.querySelectorAll("button.btn[style='width: 102px;']").forEach(node => {
  clickfndesc = node.getAttribute("onclick");
  if (clickfndesc) {
    qid = getparam(clickfndesc);
    $.ajax({
      url: "/exam/a/question/questionCollect/delCollectWrong",
      type: "post",
      data: { "question.id": qid },
      sync: true
    });
  }
});
