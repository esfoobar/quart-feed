document.addEventListener("DOMContentLoaded", function () {
  var cursorId = quartBook.cursorId;
  var ssePath = "/sse?cursor_id=" + cursorId.toString();
  var es = new EventSource(ssePath);

  postHtml = function (data) {
    const HTMLmarkup = `
    <div class="media" id="post-${data.post_uid}">
      <div class="media-left">
        <a href="${data.user_profile_url}">
          <img class="media-object" src="${data.user_image}" alt="${data.username}">
        </a>
      </div>
      <div class="media-body">
        <a href="${data.user_profile_url}">
          <div class="media-username">@${data.username}</div>
        </a>      
        <div class="media-body-text" id="post-text-${data.post_uid}">${data.body}</div>
        <div class="media-body-datetime">
          <span id="post-datetime-${data.post_uid}">${data.datetime}</span>&nbsp;-&nbsp;
          <a class="post-comment-link" data-post-uid="${data.post_uid}" href="#">Comment</a>&nbsp;-&nbsp;
          <a class="post-like-link" data-post-uid="${data.post_uid}" href="#">Like</a>
        </div>
        <div id="media-body-likes-list-${data.post_uid}" style="display: none">
          <span class="likes-label">Liked by</span>:
          <span class="likes-list" id="span-likes-list-${data.post_uid}">
          </span>
        </div>        
        <div class="media-body-comments-list">
          <ul id="post-${data.post_uid}-comment-list">
          </ul>
        </div>
        <div class="media-body-comment-entry" id="post-${data.post_uid}-comment" style="display: none;">
          <textarea
            name="post-comment"
            class="form-control"
            id="post-${data.post_uid}-comment-text"            
            rows="3"
            placeholder="Add your comment"></textarea>
          <button data-post-uid="${data.post_uid}" class="btn btn-primary post-comment-btn">Post</button>
        </div>
      </div>
    </div>
    <hr />
    `;

    return HTMLmarkup;
  };

  commentHtml = function (data) {
    const HTMLmarkup = `
    <li id="comment-${data.post_uid}-li">
      <span>${data.body}</span>&nbsp;-&nbsp;
      <a href="/user/${data.username}">
        <span>${data.username}</span>
      </a>
    </li>
    `;

    return HTMLmarkup;
  };

  likeHtml = function (data) {
    const HTMLmarkup = `
    <span class="likes-list-item" id="span-likes-list-item-${data.like_uid}">
      <a href="/user/${data.username}">
        <span>${data.username}</span>
      </a>
    </span>
    `;

    return HTMLmarkup;
  };

  es.addEventListener("new_post", function (e) {
    var messages_dom = document.getElementById("posts");
    var message_dom = document.createElement("text");
    message_dom.innerHTML = postHtml(JSON.parse(e.data)).trim();
    messages_dom.prepend(message_dom);
  });

  es.addEventListener("new_comment", function (e) {
    var commentObject = JSON.parse(e.data);
    var parentPostUid = commentObject.parent_post_uid;
    var comments_list_dom = document.getElementById(
      "post-" + parentPostUid + "-comment-list"
    );
    var comment_dom = document.createElement("text");
    comment_dom.innerHTML = commentHtml(commentObject).trim();
    comments_list_dom.append(comment_dom);
  });

  es.addEventListener("new_like", function (e) {
    var likeObject = JSON.parse(e.data);
    var postUid = likeObject.post_uid;
    var likes_list_container_dom = document.getElementById(
      "media-body-likes-list-" + postUid
    );
    likes_list_container_dom.style.display = "block";
    var likes_list_dom = document.getElementById("span-likes-list-" + postUid);
    var like_dom = document.createElement("text");
    like_dom.innerHTML = likeHtml(likeObject).trim();
    likes_list_dom.append(like_dom);
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

  document.addEventListener("click", function (e) {
    if (e.target && e.target.classList.contains("post-comment-link")) {
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

    if (e.target && e.target.classList.contains("post-comment-btn")) {
      var postUid = e.target.dataset.postUid;
      var postCommentTextElement = document.getElementById(
        "post-" + postUid + "-comment-text"
      );
      var postCommentText = postCommentTextElement.value;
      var postComment = document.getElementById("post-" + postUid + "-comment");

      fetch("/comment", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          post_uid: postUid,
          comment: postCommentText,
          csrf_token: document.getElementsByName("csrf_token")[0].value,
        }),
      });

      postCommentTextElement.value = "";
      postComment.style.display = "none";
      e.preventDefault();
    }

    if (e.target && e.target.classList.contains("post-like-link")) {
      var postUid = e.target.dataset.postUid;

      fetch("/like", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          post_uid: postUid,
          csrf_token: document.getElementsByName("csrf_token")[0].value,
        }),
      });

      e.preventDefault();
    }
  });
});
