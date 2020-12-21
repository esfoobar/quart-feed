document.addEventListener("DOMContentLoaded", function () {
  var cursorId = quartBook.cursorId;
  var ssePath = "/sse?cursor_id=" + cursorId.toString();
  var es = new EventSource(ssePath);

  postHtml = function(data) {
    const HTMLmarkup = `
    <div class="media" id="post-${ data.id }">
      <div class="media-left">
        <a href="${ data.username }">
          <img class="media-object" src="${ data.user_image }" alt="${ data.username }">
        </a>
      </div>
      <div class="media-body">
        <div class="media-body-text">${ data.body }</div>
        <div class="media-body-datetime">${ data.datetime }</div>
      </div>
    </div>
    <hr />
    `;

    return HTMLmarkup;
  }

  htmlToElements = function(html) {
    var template = document.createElement('template');
    template.innerHTML = html;
    return template.content.childNodes;    
  }

  es.onmessage = function (event) {
    var messages_dom = document.getElementById("posts");
    var message_dom = document.createElement("text");
    var content_dom = document.createTextNode(
      "Received: " + event.data + ", Type:" + event.type
    );
    // console.log("event:", event);
    message_dom.appendChild(content_dom);
    messages_dom.appendChild(message_dom);
  };

  es.addEventListener("new_post", function (e) {
    var messages_dom = document.getElementById("posts");
    var message_dom = document.createElement("text");
    message_dom.innerHTML = (postHtml(JSON.parse(e.data))).trim();
    messages_dom.prepend(message_dom);
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
