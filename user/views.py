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
import os
from werkzeug.utils import secure_filename
from sqlalchemy import select

if TYPE_CHECKING:
    from quart.wrappers.response import Response

from user.models import user_table, get_user_by_username
from relationship.models import relationship_table, existing_relationship
from user.decorators import login_required
from settings import UPLOAD_FOLDER
from utilities.imaging import thumbnail_process

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
            user = await get_user_by_username(conn, username)
            if user and user["id"]:
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
        user = await get_user_by_username(conn, form.get("username"))
        if not user:
            error = "User not found"
        # check the password
        elif not pbkdf2_sha256.verify(password, user.get("password")):
            error = "User not found"

        if not error:
            # login the user
            if not current_app.testing:
                del session["csrf_token"]

            session["user_id"] = user.get("id")
            session["username"] = user.get("username")

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


@user_app.route("/profile/edit", methods=["GET", "POST"])
@login_required
async def profile_edit() -> Union[str, "Response"]:
    error: str = ""
    csrf_token: uuid.UUID = uuid.uuid4()

    # grab the user's details
    conn = current_app.sac
    profile_user = await get_user_by_username(conn, session["username"])

    if request.method == "GET":
        session["csrf_token"] = str(csrf_token)

    if request.method == "POST":
        form: dict = await request.form
        form_username = form.get("username", "")

        if not form_username:
            error = "Please enter username"

        if (
            session.get("csrf_token") != form.get("csrf_token")
            and not current_app.testing
        ):
            error = "Invalid POST contents"

        # check if the username exists if username changed
        if not error and session["username"] != form_username:
            user = await get_user_by_username(conn, form_username)
            if user and user["id"]:
                error = "Username already exists"

        # image upload (skip if testing)
        changed_image: bool = False
        if not current_app.testing:
            files = await request.files
            profile_image = files.get("profile_image")

            # if no filename, no file was uploaded
            if profile_image.filename:
                filename = (
                    str(uuid.uuid4()) + "-" + secure_filename(profile_image.filename)
                )
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                profile_image.save(file_path)
                image_uid = thumbnail_process(
                    file_path, "user", str(profile_user["id"])
                )
                changed_image = True

        # edit the profile
        if not error:
            if not current_app.testing:
                del session["csrf_token"]

            profile_user["username"] = form_username

            if changed_image:
                profile_user["image"] = image_uid

            # delete the profile image_urls before updating
            del profile_user["image_url_raw"]
            del profile_user["image_url_xlg"]
            del profile_user["image_url_lg"]
            del profile_user["image_url_sm"]

            stmt = user_table.update(user_table.c.id == profile_user["id"]).values(
                profile_user
            )
            result = await conn.execute(stmt)
            await conn.execute("commit")

            # update session with new username
            session["username"] = form_username

            # update session
            await flash("Profile edited")
            return redirect(url_for(".profile", username=profile_user["username"]))
        else:
            session["csrf_token"] = str(csrf_token)

    return await render_template(
        "user/profile_edit.html",
        error=error,
        profile_user=profile_user,
        csrf_token=csrf_token,
    )


@user_app.route("/user/<username>")
@login_required
async def profile(username) -> Union[str, "Response"]:
    conn = current_app.sac

    # fetch the user
    user = await get_user_by_username(conn, username)

    # user not found
    if not user:
        abort(404)

    relationship: str = ""

    # see if we're looking at our own profile
    if user["id"] == session.get("user_id"):
        relationship = "self"
    else:
        if await existing_relationship(conn, session.get("user_id"), user["id"]):
            relationship = "following"
        else:
            relationship = "not_following"

    return await render_template(
        "user/profile.html", user=user, relationship=relationship
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
