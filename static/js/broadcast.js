document.addEventListener("DOMContentLoaded", function () {
  var cursorId = quartBook.cursorId;
  var ssePath = "/sse?cursor_id=" + cursorId.toString();
  var es = new EventSource(ssePath);

  es.onmessage = function (event) {
    var messages_dom = document.getElementById("posts");
    var message_dom = document.createElement("li");
    var content_dom = document.createTextNode(
      "Received: " + event.data + ", Type:" + event.type
    );
    // console.log("event:", event);
    message_dom.appendChild(content_dom);
    messages_dom.appendChild(message_dom);
  };

  es.addEventListener("new_post", function (e) {
    console.log("Event:", json.parse(e.data));
  });

  document.getElementById("send").onclick = function () {
    fetch("/post", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        post: document.getElementsByName("post")[0].value,
        csrf_token: document.getElementsByName("csrf_token")[0].value,
      }),
    });
    document.getElementsByName("post")[0].value = "";
  };
});
