document.addEventListener("DOMContentLoaded", function () {
  var cursorId = quartBook.cursorId;
  var ssePath = "/sse?cursor_id=" + cursorId.toString();
  var es = new EventSource(ssePath);

  postHtml = function(data) {
    const HTMLmarkup = `
    <div class="media" id="post-${ post_id }">
      <div class="media-left">
        <a href="${ profile_url }">
          <img class="media-object" src="${ profile_user_image }" alt="${ username }">
        </a>
      </div>
      <div class="media-body">
        <div class="media-body-text">${ post.body }</div>
        <div class="media-body-datetime">${
          post_datetime }</div>
      </div>
    </div>
    <hr />
    `;

    return HTMLmarkup;
  }

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
    var messages_dom = document.getElementById("posts");
    var message_dom = document.createElement("li");
    console.log("Event:", JSON.parse(e.data));
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
