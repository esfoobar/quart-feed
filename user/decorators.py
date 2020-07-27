from functools import wraps
from quart import session, request, redirect, url_for


def login_required(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect(url_for("user_app.login", next=request.url))
        return await f(*args, **kwargs)

    return decorated_function
