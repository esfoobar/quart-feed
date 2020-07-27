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
from passlib.hash import pbkdf2_sha256
import uuid
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from quart.wrappers.response import Response

from user.models import user_table, get_user_by_username
from relationship.models import relationship_table, existing_relationship
from user.decorators import login_required

user_app = Blueprint("user_app", __name__)


@user_app.route("/register", methods=["GET", "POST"])
async def register() -> Union[str, "Response"]:
    error: str = ""
    username: str = ""
    password: str = ""
    csrf_token: uuid.UUID = uuid.uuid4()

    if request.method == "GET":
        session["csrf_token"] = str(csrf_token)

    if request.method == "POST":
        form: dict = await request.form
        username = form.get("username", "")
        password = form.get("password", "")

        if not username or not password:
            error = "Please enter username and password"

        if (
            session.get("csrf_token") != form.get("csrf_token")
            and not current_app.testing
        ):
            error = "Invalid POST contents"

        conn = current_app.sac

        # check if the user exists
        if not error:
            user_row = await get_user_by_username(conn, username)
            if user_row and user_row.id:
                error = "Username already exists"

        # register the user
        if not error:
            if not current_app.testing:
                del session["csrf_token"]

            hash: str = pbkdf2_sha256.hash(password)
            stmt = user_table.insert().values(username=username, password=hash)
            result = await conn.execute(stmt)
            await conn.execute("commit")
            await flash("You have been registered, please login")
            return redirect(url_for(".login"))
        else:
            session["csrf_token"] = str(csrf_token)

    return await render_template(
        "user/register.html", error=error, username=username, csrf_token=csrf_token
    )


@user_app.route("/login", methods=["GET", "POST"])
async def login() -> Union[str, "Response"]:
    error: str = ""
    username: str = ""
    password: str = ""
    csrf_token: uuid.UUID = uuid.uuid4()

    if request.method == "GET":
        session["csrf_token"] = str(csrf_token)
        if request.args.get("next"):
            session["next"] = request.args.get("next")

    if request.method == "POST":
        form: dict = await request.form
        username = form.get("username", "")
        password = form.get("password", "")

        if not username or not password:
            error = "Please enter username and password"

        if (
            session.get("csrf_token") != form.get("csrf_token")
            and not current_app.testing
        ):
            error = "Invalid POST contents"

        conn = current_app.sac

        # check if the user exists
        user_row = await get_user_by_username(conn, form.get("username"))
        if not user_row:
            error = "User not found"
        # check the password
        elif not pbkdf2_sha256.verify(password, user_row.password):
            error = "User not found"

        if not error:
            # login the user
            if not current_app.testing:
                del session["csrf_token"]

            session["user_id"] = user_row.id
            session["username"] = user_row.username

            if "next" in session:
                next = session.get("next")
                session.pop("next")
                return redirect(next)
            else:
                return "User logged in"

        else:
            session["csrf_token"] = str(csrf_token)

    return await render_template(
        "user/login.html", error=error, username=username, csrf_token=csrf_token
    )


@user_app.route("/logout", methods=["GET"])
async def logout() -> "Response":
    del session["user_id"]
    del session["username"]
    return redirect(url_for(".login"))


@user_app.route("/user/edit")
@login_required
async def profile_edit() -> Union[str, "Response"]:
    error: str = ""
    username: str = ""
    csrf_token: uuid.UUID = uuid.uuid4()

    if request.method == "GET":
        session["csrf_token"] = str(csrf_token)

    if request.method == "POST":
        form: dict = await request.form
        username = form.get("username", "")

        if not username:
            error = "Please enter username"

        if (
            session.get("csrf_token") != form.get("csrf_token")
            and not current_app.testing
        ):
            error = "Invalid POST contents"

        conn = current_app.sac

        # check if the user exists
        if not error:
            user_row = await get_user_by_username(conn, username)
            if user_row and user_row.id:
                error = "Username already exists"

        # register the user
        if not error:
            if not current_app.testing:
                del session["csrf_token"]

            stmt = user_table.update(username=session["username"]).values(
                username=username
            )
            result = await conn.execute(stmt)
            await conn.execute("commit")
            await flash("Profile edited")
        else:
            session["csrf_token"] = str(csrf_token)

    return await render_template(
        "user/profile_edit.html", error=error, username=username, csrf_token=csrf_token
    )


@user_app.route("/user/<username>")
@login_required
async def profile(username) -> Union[str, "Response"]:
    conn = current_app.sac

    # fetch the user
    user_row = await get_user_by_username(conn, username)

    # user not found
    if not user_row:
        abort(404)

    relationship: str = ""

    # see if we're looking at our own profile
    if user_row.id == session.get("user_id"):
        relationship = "self"
    else:
        if await existing_relationship(conn, session.get("user_id"), user_row.id):
            relationship = "following"
        else:
            relationship = "not_following"

    return await render_template(
        "user/profile.html", username=username, relationship=relationship
    )


@user_app.route("/user/list")
@login_required
async def user_list() -> Union[str, "Response"]:
    conn = current_app.sac
    username_query = select([user_table.c.username])
    result = await conn.execute(username_query)
    for row in await result.fetchall():
        print(row)

    return "user list"
