/*
 * Filter rows in visualable table
 */

function filter(text) {
  document.querySelectorAll("tbody tr").forEach(el => {
    if (el.innerText.search(text) === -1) {
      el.className = "hidden";
    } else {
      el.className = "";
    }
  });
}

function filter_any(texts) {
  document.querySelectorAll("tbody tr").forEach(el => {
    let has_any = false;
    texts.forEach(text => {
      if (el.innerText.search(text) !== -1) {
        has_any = true;
      }
    });

    if (!has_any) {
      el.className = "hidden";
    } else {
      el.className = "";
    }
  });
}

function reset() {
  document.querySelectorAll("tbody tr").forEach(el => {
    el.className = "";
  });
}

function filter_homework() {
  filter("2见习医院10");
}
