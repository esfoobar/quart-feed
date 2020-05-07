from quart import (
    Blueprint,
    current_app,
    render_template,
    session,
    redirect,
    url_for,
    current_app,
    abort,
    request,
    flash,
)
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from quart.wrappers.response import Response

from user.models import user_table, get_user_by_username
from relationship.models import relationship_table, existing_relationship
from user.decorators import login_required

relationship_app = Blueprint("relationship_app", __name__)


@relationship_app.route("/add_friend/<username>", methods=["GET"])
@login_required
async def add_friend(username) -> Union[str, "Response"]:
    conn = current_app.sac
    referrer = request.referrer
    logged_user_id = session.get("user_id")

    # check if user exists
    to_user_row = await get_user_by_username(conn, username)
    if not to_user_row:
        abort(404)

    # check if the relationship already exists
    if not await existing_relationship(conn, logged_user_id, to_user_row.id):
        # store the relationship
        stmt = relationship_table.insert().values(
            fm_user_id=logged_user_id, to_user_id=to_user_row.id
        )
        result = await conn.execute(stmt)
        await conn.execute("commit")
        await flash(f"Followed {to_user_row.username}")

    # redirect back to the calling url
    return redirect(referrer)


@relationship_app.route("/remove_friend/<username>", methods=["GET"])
@login_required
async def remove_friend(username) -> Union[str, "Response"]:
    conn = current_app.sac
    referrer = request.referrer
    logged_user_id = session.get("user_id")

    # check if user exists
    to_user_row = await get_user_by_username(conn, username)
    if not to_user_row:
        abort(404)

    # check if the relationship already exists
    if await existing_relationship(conn, logged_user_id, to_user_row.id):
        # remove the relationship
        stmt = relationship_table.delete().where(
            (relationship_table.c.fm_user_id == logged_user_id)
            & (relationship_table.c.to_user_id == to_user_row.id)
        )
        result = await conn.execute(stmt)
        await conn.execute("commit")
        await flash(f"Unfollowed {to_user_row.username}")

    # redirect back to the calling url
    return redirect(referrer)
