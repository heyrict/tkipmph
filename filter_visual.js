/*
 * Filter rows in visualable table
 */

_C_QUERY = "tbody tr";
_C_ORIGCLS = "";

function init_style() {
  let node = document.createElement("style");
  let head = document.head;
  let style = `.hidden { display: none}`;
  node.type = "text/css";
  node.appendChild(document.createTextNode(style));
  head.appendChild(node);
}

function filter(text) {
  document.querySelectorAll(_C_QUERY).forEach(el => {
    if (el.innerText.search(text) === -1) {
      el.className = _C_ORIGCLS + " hidden";
    } else {
      el.className = _C_ORIGCLS;
    }
  });
}

function filter_any(texts) {
  document.querySelectorAll(_C_QUERY).forEach(el => {
    let has_any = false;
    texts.forEach(text => {
      if (el.innerText.search(text) !== -1) {
        has_any = true;
      }
    });

    if (!has_any) {
      el.className = _C_ORIGCLS + " hidden";
    } else {
      el.className = _C_ORIGCLS;
    }
  });
}

function reset() {
  document.querySelectorAll(_C_QUERY).forEach(el => {
    el.className = _C_ORIGCLS + "";
  });
}

function filter_homework() {
  filter("2见习医院10");
}
