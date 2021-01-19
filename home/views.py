from quart import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash,
    abort,
    make_response,
    current_app,
)
from typing import Union, TYPE_CHECKING
import uuid
import asyncio
import random
from sqlalchemy import select, desc
import arrow
import json
import logging

from .models import ServerSentEvent
from user.decorators import login_required
from post.models import feed_table, post_table, ActionType, get_latest_posts
from user.models import user_table, image_url_from_image_ts

if TYPE_CHECKING:
    from quart.wrappers.response import Response


home_app = Blueprint("home_app", __name__)


@home_app.route("/", methods=["GET"])
@login_required
async def init() -> str:
    csrf_token: uuid.UUID = uuid.uuid4()
    session["csrf_token"] = str(csrf_token)
    conn = current_app.sac

    cursor_id: int = 0
    posts: list = []

    post_results = await get_latest_posts(conn, session["user_id"])
    for row in post_results:
        post = post_context(row)
        posts.append(post)

        if cursor_id == 0:
            cursor_id = row["feed_id"]

    return await render_template(
        "home/init.html", posts=posts, csrf_token=csrf_token, cursor_id=cursor_id
    )


@home_app.route("/sse")
@login_required
async def sse() -> "Response":
    user_id = session.get("user_id")
    cursor_id = int(request.args.get("cursor_id"))
    conn = current_app.sac

    async def send_events(conn, user_id, cursor_id):
        while True:
            try:
                # get all the feed items greater than that cursor_id
                recent_posts = await get_latest_posts(
                    conn, user_id, from_post_id=cursor_id, num_posts=1
                )

                if len(recent_posts) > 0:
                    row = recent_posts[0]

                    event = ServerSentEvent(
                        json.dumps(post_context(row)), event="new_post", id=id
                    )

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
        "id": row["feed_id"],
        "uid": row["post_uid"],
        "body": row["post_body"],
        "datetime": arrow.get(row["feed_updated"]).humanize(),
        "username": row["user_username"],
        "user_profile_url": f"/user/{row['user_username']}",
        "user_image": user_images["image_url_lg"],
    }

    return post
