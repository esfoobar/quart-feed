from quart import (
    Blueprint,
    render_template,
    request,
    session,
    make_response,
    current_app,
)
from typing import Union, TYPE_CHECKING
import uuid
import asyncio
from sqlalchemy import select, desc
import arrow
import json
import logging

from .models import ServerSentEvent
from user.decorators import login_required
from post.models import (
    get_comment_parent_uid,
    get_last_feed_id,
    ActionType,
    get_latest_posts,
    get_post_comments,
)
from user.models import user_table, image_url_from_image_ts

if TYPE_CHECKING:
    from quart.wrappers.response import Response


home_app = Blueprint("home_app", __name__)


@home_app.route("/", methods=["GET"])
@login_required
async def init() -> str:
    csrf_token: uuid.UUID = uuid.uuid4()
    session["csrf_token"] = str(csrf_token)
    conn = current_app.dbc

    posts: list = []

    post_results = await get_latest_posts(conn, session["user_id"])
    for row in post_results:
        # get post data
        post = post_context(row)

        # get comments
        comments = await get_post_comments(conn, post["post_uid"])

        post["comments"] = []
        for comment in comments:
            # not needed for initial load
            comment = dict(comment)
            comment["post_parent_post_uid"] = None
            post["comments"].append(comment_context(comment))

        posts.append(post)

    # Get last feed id for user
    cursor_id = await get_last_feed_id(conn, session["user_id"])

    return await render_template(
        "home/init.html", posts=posts, csrf_token=csrf_token, cursor_id=cursor_id
    )


@home_app.route("/sse")
@login_required
async def sse() -> "Response":
    user_id = session.get("user_id")
    cursor_id = int(request.args.get("cursor_id"))
    conn = current_app.dbc

    async def send_events(conn, user_id, cursor_id):
        while True:
            try:
                # get all the feed items greater than that cursor_id
                recent_posts = await get_latest_posts(
                    conn, user_id, from_post_id=cursor_id, num_posts=1
                )

                if len(recent_posts) > 0:
                    row = recent_posts[0]
                    action_type = row["feed_action"]
                    event = None

                    if action_type == ActionType.new_post:
                        post_obj = post_context(row)
                        event = ServerSentEvent(
                            json.dumps(post_obj), event="new_post", id=id
                        )

                    if action_type == ActionType.new_comment:
                        # get post parent uid
                        comment = dict(row)

                        parent_post_uid = await get_comment_parent_uid(
                            conn, post_id=comment["post_id"]
                        )
                        comment["post_parent_post_uid"] = parent_post_uid

                        comment_obj = comment_context(comment)
                        event = ServerSentEvent(
                            json.dumps(comment_obj), event="new_comment", id=id
                        )

                    if event:
                        yield event.encode()

                    # update the cursor_id
                    cursor_id = row["feed_id"]

                # wait 10 seconds
                await asyncio.sleep(1)

            except asyncio.CancelledError as error:
                logging.error("Exception:" + str(error))

    response = await make_response(
        send_events(conn, user_id, cursor_id),
        {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Transfer-Encoding": "chunked",
        },
    )
    response.timeout = None
    return response


def post_context(row) -> dict:
    user_images = image_url_from_image_ts(row["user_id"], row["user_image"])
    post: dict = {
        "post_uid": row["post_uid"],
        "parent_post_id": row["post_parent_post_id"],
        "body": row["post_body"],
        "datetime": arrow.get(row["feed_updated"]).humanize(),
        "username": row["user_username"],
        "user_profile_url": f"/user/{row['user_username']}",
        "user_image": user_images["image_url_lg"],
    }

    return post


def comment_context(row) -> dict:
    comment: dict = {
        "post_uid": row["post_uid"],
        "parent_post_uid": row["post_parent_post_uid"],
        "body": row["post_body"],
        "username": row["user_username"],
    }

    return comment
