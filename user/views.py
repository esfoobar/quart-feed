from quart import Blueprint, current_app
from sqlalchemy.sql import select

from user.models import user_table

user_app = Blueprint("user_app", __name__)


@user_app.route("/register")
async def register():
    return "<h1>User Registration</h1>"
