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

if TYPE_CHECKING:
    from quart.wrappers.response import Response


home_app = Blueprint("home_app", __name__)


@home_app.route("/", methods=["GET"])
async def register() -> Union[str, "Response"]:
    return "<h1>Welcome to QuartFeed</h1>"
