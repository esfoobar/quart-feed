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

from user.models import user_table
from relationship.models import relationship_table
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

        # check if the user exists
        if not error:
            conn = current_app.sac
            stmt = user_table.select().where(
                user_table.c.username == form.get("username")
            )
            result = await conn.execute(stmt)
            row = await result.fetchone()
            if row and row.id:
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

        # check if the user exists
        conn = current_app.sac
        stmt = user_table.select().where(user_table.c.username == form.get("username"))
        result = await conn.execute(stmt)
        row = await result.fetchone()
        if not row:
            error = "User not found"
        # check the password
        elif not pbkdf2_sha256.verify(password, row.password):
            error = "User not found"

        if not error:
            # login the user
            if not current_app.testing:
                del session["csrf_token"]

            session["user_id"] = row.id
            session["username"] = row.username

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


@user_app.route("/<username>")
@login_required
async def profile(username) -> Union[str, "Response"]:
    # fetch the user
    conn = current_app.sac
    stmt = user_table.select().where(user_table.c.username == username)
    result = await conn.execute(stmt)
    profile_user = await result.fetchone()

    # user not found
    if not profile_user:
        abort(404)

    relationship: str = ""

    # see if we're looking at our own profile
    if profile_user.id == session.get("user_id"):
        relationship = "self"
    else:
        stmt = relationship_table.select().where(
            (relationship_table.c.fm_user_id == session.get("user_id"))
            & (relationship_table.c.to_user_id == profile_user.id)
        )
        result = await conn.execute(stmt)
        relationship_record = await result.fetchone()
        if relationship_record:
            relationship = "following"
        else:
            relationship = "not_following"

    return await render_template(
        "user/profile.html", username=username, relationship=relationship
    )
