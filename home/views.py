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

from .models import ServerSentEvent
from user.decorators import login_required
from post.models import feed_table, post_table, ActionType
from user.models import user_table, image_url_from_image_ts

if TYPE_CHECKING:
    from quart.wrappers.response import Response


home_app = Blueprint("home_app", __name__)


@home_app.route("/", methods=["GET"])
@login_required
async def init() -> Union[str, "Response"]:
    csrf_token: uuid.UUID = uuid.uuid4()
    session["csrf_token"] = str(csrf_token)
    conn = current_app.sac

    # get the last 10 posts in feed in reverse order and
    # pass to the context the last id as cursor_id
    latest_posts_query = (
        select(
            [
                post_table.c.id,
                post_table.c.uid,
                post_table.c.body,
                post_table.c.updated,
                user_table.c.username,
                user_table.c.id,
                user_table.c.image,
            ]
        )
        .where(
            (feed_table.c.post_id == post_table.c.id)
            & (feed_table.c.to_user_id == session["user_id"])
            & (feed_table.c.fm_user_id == user_table.c.id)
            & (feed_table.c.action == ActionType.new_post)
        )
        .order_by(desc(feed_table.c.updated))
        .limit(10)
        .offset(0)
        .apply_labels()
    )
    result = await conn.execute(latest_posts_query)

    posts: list = []
    cursor_id: int = 0

    for row in await result.fetchall():
        user_images = image_url_from_image_ts(row["user_id"], row["user_image"])

        post: dict = {
            "id": row["post_id"],
            "uid": row["post_uid"],
            "body": row["post_body"],
            "datetime": arrow.get(row["post_updated"]).humanize(),
            "username": row["user_username"],
            "user_image": user_images["image_url_lg"],
        }
        posts.append(post)

        if cursor_id == 0:
            cursor_id = row["post_id"]

    # on broadcast.js set that variable as a window object on namespace

    # then broadcast.js picks that up and sends to /sse as a param

    return await render_template(
        "home/init.html", posts=posts, csrf_token=csrf_token, cursor_id=cursor_id
    )


@home_app.route("/sse")
@login_required
async def sse():
    username = session.get("username")
    cursor_id = request.args.get("cursor_id")

    async def send_events(username):
        while True:
            try:
                # get all the feed items greater than that cursor_id

                # update the cursor_id

                # get data from database
                id = str(random.sample(range(1, 100), 1))
                data = {"post_id": id, "message": f"Hello {username}"}
                event = ServerSentEvent(data, event="new_like", id=id)

                # print("event-sse:", event.encode())
                yield event.encode()
                await asyncio.sleep(10)
            except asyncio.CancelledError as error:
                print("Exception:", error)

    response = await make_response(
        send_events(username),
        {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Transfer-Encoding": "chunked",
        },
    )
    response.timeout = None
    return response
