from quart import (
    Blueprint,
    current_app,
    render_template,
    session,
    redirect,
    url_for,
    current_app,
    abort,
)
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from quart.wrappers.response import Response

from user.models import user_table
from relationship.models import relationship_table

relatiionship_app = Blueprint("relationship_app", __name__)


@relatiionship_app.route("/add_friend/<username>", methods=["GET",])
async def add_friend() -> Union[str, "Response"]:
