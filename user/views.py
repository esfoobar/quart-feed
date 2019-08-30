from quart import Blueprint, current_app, render_template, request

from user.models import user_table

user_app = Blueprint("user_app", __name__)


@user_app.route("/register", methods=["GET", "POST"])
async def register() -> str:
    error: str = ""
    user_username: str = ""
    user_password: str = ""
    if request.method == "POST":
        form = await request.form
        user_username = form.get("user_username")
        user_password = form.get("user_password")
        if not user_username or not user_password:
            error = "Please enter username and password"
        else:
            # check if the user exists
            # register the user
            pass
    return await render_template(
        "user/register.html", error=error, user_username=user_username
    )
