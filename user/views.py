from quart import Blueprint, current_app, render_template, request
from passlib.hash import pbkdf2_sha256

from user.models import user_table

user_app = Blueprint("user_app", __name__)


@user_app.route("/register", methods=["GET", "POST"])
async def register() -> str:
    error: str = ""
    user_username: str = ""
    user_password: str = ""
    if request.method == "POST":
        form: dict = await request.form
        user_username = form.get("user_username", "")
        user_password = form.get("user_password", "")
        if not user_username or not user_password:
            error = "Please enter username and password"
        else:
            # check if the user exists
            # register the user
            hash: str = pbkdf2_sha256.hash(user_password)
            conn = current_app.sac
            stmt = user_table.insert().values(username=user_username, password=hash)
            result = await conn.execute(stmt)
            await conn.execute("commit")
    return await render_template(
        "user/register.html", error=error, user_username=user_username
    )
