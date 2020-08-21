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
    jsonify,
)
import uuid
from typing import Union, Tuple, TYPE_CHECKING
from sqlalchemy import select

if TYPE_CHECKING:
    from quart.wrappers.response import Response

from post.models import post_table, like_table, feed_table, ActionType
from relationship.models import get_user_followers
from user.decorators import login_required

post_app = Blueprint("post_app", __name__)


@post_app.route("/post", methods=["POST"])
@login_required
async def post() -> Tuple["Response", int]:
    error: bool = False

    if request.method == "POST":
        data = await request.get_json()
        post = data.get("post", "")

        if not post or post == "":
            error = True
            await flash("Please enter a post text")

        if (
            session.get("csrf_token") != data.get("csrf_token")
            and not current_app.testing
        ):
            error = True
            await flash("Invalid POST contents")

        if not error:
            conn = current_app.sac

            # insert on post table
            post_record = {
                "uid": str(uuid.uuid4()),
                "parent_post_id": None,
                "body": post,
                "user_id": session.get("user_id"),
            }
            stmt = post_table.insert().values(**post_record)
            result = await conn.execute(stmt)
            await conn.execute("commit")
            post_record_id = result.lastrowid

            # get all the followers, where to_user_id = session user id
            followers = await get_user_followers(conn, session.get("user_id"))

            # insert on feed table
            for follower in followers:
                # insert on feed table for all followers
                feed_record = {
                    "post_id": post_record_id,
                    "action": ActionType.new_post,
                    "fm_user_id": session.get("user_id"),
                    "to_user_id": follower["id"],
                }
                stmt_1 = feed_table.insert().values(**feed_record)
                result = await conn.execute(stmt_1)
                await conn.execute("commit")

            # add it for the same user
            feed_record = {
                "post_id": post_record_id,
                "action": ActionType.new_post,
                "fm_user_id": session.get("user_id"),
                "to_user_id": session.get("user_id"),
            }
            stmt_2 = feed_table.insert().values(**feed_record)
            result = await conn.execute(stmt_2)
            await conn.execute("commit")

    return jsonify({"result": "ok"}), 200
