from quart import Blueprint, current_app, render_template, request

from user.models import user_table

user_app = Blueprint("user_app", __name__)


@user_app.route("/register", methods=["GET", "POST"])
async def register() -> str:
    error: str = ""
    username: str = ""
    password: str = ""
    if request.method == "POST":
        form = await request.form
        username = form.get("username")
        password = form.get("password")
        if not username or not password:
            error = "Please enter username and password"
        else:
            # check if the user exists
            # register the user
            pass
    return await render_template("user/register.html", error=error, username=username)
