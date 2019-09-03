from quart import Blueprint, current_app, render_template, request, session
from passlib.hash import pbkdf2_sha256
import uuid

from user.models import user_table

user_app = Blueprint("user_app", __name__)


@user_app.route("/register", methods=["GET", "POST"])
async def register() -> str:
    error: str = ""
    user_username: str = ""
    user_password: str = ""
    csrf_token: uuid.UUID = uuid.uuid4()

    if request.method == "GET":
        session["csrf_token"] = str(csrf_token)

    if request.method == "POST":
        form: dict = await request.form
        user_username = form.get("user_username", "")
        user_password = form.get("user_password", "")

        if not user_username or not user_password:
            error = "Please enter username and password"

        if session.get("csrf_token") != form.get("csrf_token"):
            error = "Invalid POST contents"

        # check if the user exists
        conn = current_app.sac
        stmt = user_table.select().where(
            user_table.c.username == form.get("user_username")
        )
        result = await conn.execute(stmt)
        row = await result.fetchone()
        if row and row.id:
            error = "Username already exists"

        if not error:
            # register the user
            del session["csrf_token"]
            hash: str = pbkdf2_sha256.hash(user_password)
            stmt = user_table.insert().values(username=user_username, password=hash)
            result = await conn.execute(stmt)
            await conn.execute("commit")
        else:
            session["csrf_token"] = str(csrf_token)

    return await render_template(
        "user/register.html",
        error=error,
        user_username=user_username,
        csrf_token=csrf_token,
    )
