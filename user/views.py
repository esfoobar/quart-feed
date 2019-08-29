from quart import Blueprint, current_app, render_template, request
from sqlalchemy.sql import select
from werkzeug.security import generate_password_hash

from user.models import user_table

user_app = Blueprint("user_app", __name__)


@user_app.route("/register", methods=["GET", "POST"])
async def register():
    error = None
    user_email = None
    user_password = None
    if request.method == "POST":
        form = await request.form
        user_email = form.get("user_email")
        user_password = form.get("user_password")
        if not user_email or not user_password:
            error = "Please enter email and password"
        else:
            # check if the user exists
            # register the user
            breakpoint()
            hashed_password = generate_password_hash(form.get("password"))
            pass
    return await render_template(
        "user/register.html", error=error, user_email=user_email
    )
