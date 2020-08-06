from quart import (
    Blueprint,
    current_app,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash,
    current_app,
    abort,
)
import uuid
from typing import Union, TYPE_CHECKING
from sqlalchemy import select

if TYPE_CHECKING:
    from quart.wrappers.response import Response

from post.models import post_table, like_table, feed_table

post_app = Blueprint("post_app", __name__)


@post_app.route("/post", methods=["POST"])
async def post() -> Union[str, "Response"]:
    error: bool = False

    if request.method == "POST":
        form: dict = await request.form
        post = form.get("post", "")

        if not post or post == "":
            error = True
            await flash("Please enter a post text")

        if (
            session.get("csrf_token") != form.get("csrf_token")
            and not current_app.testing
        ):
            error = True
            await flash("Invalid POST contents")

        if not error:
            conn = current_app.sac

            # check if the user exists
            # user = await get_user_by_username(conn, form.get("username"))
            # if not user:
            #     error = "User not found"

    return redirect(url_for("home_app.init"))
