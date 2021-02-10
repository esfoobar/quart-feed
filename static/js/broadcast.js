document.addEventListener("DOMContentLoaded", function () {
  var cursorId = quartBook.cursorId;
  var ssePath = "/sse?cursor_id=" + cursorId.toString();
  var es = new EventSource(ssePath);

  postHtml = function(data) {
    const HTMLmarkup = `
    <div class="media" id="post-${ data.post_uid }">
      <div class="media-left">
        <a href="${ data.user_profile_url }">
          <img class="media-object" src="${ data.user_image }" alt="${ data.username }">
        </a>
      </div>
      <div class="media-body">
        <a href="${ data.user_profile_url }">
          <div class="media-username">@${ data.username }</div>
        </a>      
        <div class="media-body-text" id="post-text-${ data.post_uid }">${ data.body }</div>
        <div class="media-body-datetime">
          <span id="post-datetime-${ data.post_uid }">${ data.datetime }</span>&nbsp;-&nbsp;
          <a class="post-comment-link" data-post-uid="${ data.post_uid }" href="#">Comment</a>
        </div>
        <div class="media-body-comments-list">
          <ul id="post-${ post.post_uid }-comment-list">
          </ul>
        </div>
        <div class="media-body-comment-entry" id="post-${ data.post_uid }-comment" style="display: none;">
          <textarea
            name="post-comment"
            class="form-control"            
            rows="3"
            placeholder="Add your comment"></textarea>
          <button data-post-uid="${ data.post_uid }" data-parent-post-id="${ data.post_id }" class="btn btn-primary post-comment-btn">Post</button>
        </div>
      </div>
    </div>
    <hr />
    `;

    return HTMLmarkup;
  }

  commentHtml = function(data) {
    const HTMLmarkup = `
    <li id="comment-${ data.post_uid }-li">
      <span>${ data.body }</span>&nbsp;-&nbsp;
      <a href="/user/${ data.username }">
        <span>${ data.username }</span>
      </a>
    </li>
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

  es.addEventListener("new_comment", function (e) {
    var commentObject = JSON.parse(e.data);
    var parentPostUid = commentObject.parent_post_uid;
    var comments_list_dom = document.getElementById("post-" + parentPostUid + "-comment-list");
    var comment_dom = document.createElement("text");
    comment_dom.innerHTML = (commentHtml(commentObject)).trim();
    comments_list_dom.append(comment_dom);
  });  

  document.getElementById("post").onclick = function () {
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

  document.addEventListener('click',function(e){
    if (e.target && e.target.classList.contains("post-comment-link")){
      var postUid = e.target.dataset.postUid;
      var postComment = document.getElementById("post-" + postUid + "-comment");
      if (postComment.style.display === "none") {
        postComment.style.display = "block";
        postComment.focus();
      } else {
        postComment.style.display = "none";
      }
      e.preventDefault();
     }

     if (e.target && e.target.classList.contains("post-comment-btn")){
      var postUid = e.target.dataset.postUid;
      var parentPostId = e.target.dataset.parentPostId;
      var postCommentTextElement = document.getElementById("post-" + postUid + "-comment-text");
      var postCommentText = postCommentTextElement.value;
      var postComment = document.getElementById("post-" + postUid + "-comment");

      fetch("/comment", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          parent_post_id: parentPostId,
          comment: postCommentText,
          csrf_token: document.getElementsByName("csrf_token")[0].value,
        }),
      });

      postCommentTextElement.value = "";
      postComment.style.display = "none";
      e.preventDefault();
 }
 });
});
