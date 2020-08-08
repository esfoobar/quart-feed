from quart import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash,
    abort,
)
from typing import Union, TYPE_CHECKING
import uuid

from .sse import ServerSentEvent

if TYPE_CHECKING:
    from quart.wrappers.response import Response


home_app = Blueprint("home_app", __name__)


@home_app.route("/", methods=["GET"])
async def init() -> Union[str, "Response"]:
    csrf_token: uuid.UUID = uuid.uuid4()
    session["csrf_token"] = str(csrf_token)

    return await render_template("home/init.html", csrf_token=csrf_token)


@home_app.route("/sse")
async def sse():
    async def send_events():
        while True:
            try:
                # data = await queue.get()
                # get data from database
                event = ServerSentEvent(data)
                yield event.encode()
            except asyncio.CancelledError as error:
                app.clients.remove(queue)

    response = await make_response(
        send_events(),
        {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Transfer-Encoding": "chunked",
        },
    )
    response.timeout = None
    return response
