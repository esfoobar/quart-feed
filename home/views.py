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
)
from typing import Union, TYPE_CHECKING
import uuid
import asyncio
import random

from .models import ServerSentEvent
from user.decorators import login_required

if TYPE_CHECKING:
    from quart.wrappers.response import Response


home_app = Blueprint("home_app", __name__)


@home_app.route("/", methods=["GET"])
@login_required
async def init() -> Union[str, "Response"]:
    csrf_token: uuid.UUID = uuid.uuid4()
    session["csrf_token"] = str(csrf_token)

    # get the last 10 posts in feed in reverse order and
    # pass to the context the last id as cursor_id

    # on broadcast.js set that variable as a window object on namespace

    # then broadcast.js picks that up and sends to /sse as a param

    return await render_template("home/init.html", csrf_token=csrf_token)


@home_app.route("/sse")
@login_required
async def sse():
    username = session.get("username")
    # cursor_id = request.values.get("cursor_id")

    async def send_events(username):
        while True:
            try:
                # set the last feed cursor_id from param

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
