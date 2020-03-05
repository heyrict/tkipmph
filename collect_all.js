function addcollect(questionId) {
  var personalFlag = 0;
  $.ajax({
    type: "post",
    url: "/exam/a/question/questionCollect/saveCollect",
    data: { "question.id": questionId, personalFlag: personalFlag },
    success: function(result) {
      if (result.result != "1") {
      } else {
        console.log("添加失败，原因：" + result.msg, "error");
      }
    }
  });
}

cells = document.querySelectorAll("button.cell");
qids = Array.from(cells).map(c => c.name);
qids.forEach(qid => addcollect(qid));
