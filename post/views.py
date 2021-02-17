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

from post.models import (
    get_comment_parent_uid,
    post_table,
    like_table,
    feed_table,
    ActionType,
    get_post_feed_followers,
    get_post_id_from_uid,
)
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
            await flash("Invalid user, please login")

        if not error:
            conn = current_app.dbc

            # insert on post table
            post_record = {
                "uid": str(uuid.uuid4()),
                "parent_post_id": None,
                "body": post,
                "user_id": session.get("user_id"),
            }
            post_query = post_table.insert().values(**post_record)
            result = await conn.execute(query=post_query)
            post_record_id = result

            # get all the followers, where to_user_id = session user id
            followers = await get_user_followers(conn, session.get("user_id"))

            # insert on feed table
            for follower in followers:
                # insert on feed table for all followers
                feed_record = {
                    "uid": str(uuid.uuid4()),
                    "post_id": post_record_id,
                    "action": ActionType.new_post,
                    "fm_user_id": session.get("user_id"),
                    "to_user_id": follower["id"],
                }
                follower_post_query = feed_table.insert().values(**feed_record)
                await conn.execute(query=follower_post_query)

            # add it for the same user
            feed_record = {
                "uid": str(uuid.uuid4()),
                "post_id": post_record_id,
                "action": ActionType.new_post,
                "fm_user_id": session.get("user_id"),
                "to_user_id": session.get("user_id"),
            }
            self_post_query = feed_table.insert().values(**feed_record)
            await conn.execute(query=self_post_query)

    return jsonify({"result": "ok"}), 200


@post_app.route("/comment", methods=["POST"])
@login_required
async def comment() -> Tuple["Response", int]:
    error: bool = False

    if request.method == "POST":
        breakpoint()
        data = await request.get_json()
        post_uid = data.get("post_uid", None)
        comment = data.get("comment", "")

        if not post_uid:
            error = True
            await flash("Invalid post id")

        if not comment or comment == "":
            error = True
            await flash("Please enter a comment text")

        if (
            session.get("csrf_token") != data.get("csrf_token")
            and not current_app.testing
        ):
            error = True
            await flash("Invalid user, please login")

        if not error:
            conn = current_app.dbc

            parent_post_id = await get_post_id_from_uid(conn, post_uid)

            # insert comment on post table
            post_record = {
                "uid": str(uuid.uuid4()),
                "parent_post_id": parent_post_id,
                "body": comment,
                "user_id": session.get("user_id"),
            }
            post_query = post_table.insert().values(**post_record)
            result = await conn.execute(query=post_query)
            post_record_id = result

            # get all the followers of the parent feed post
            followers = await get_post_feed_followers(conn, parent_post_id)

            # insert on feed table
            for follower in followers:
                # insert on feed table for all followers
                feed_record = {
                    "uid": str(uuid.uuid4()),
                    "post_id": post_record_id,
                    "action": ActionType.new_comment,
                    "fm_user_id": session.get("user_id"),
                    "to_user_id": follower["feed_to_user_id"],
                }
                follower_post_query = feed_table.insert().values(**feed_record)
                await conn.execute(query=follower_post_query)

    return jsonify({"result": "ok"}), 200
