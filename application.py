from quart import Quart
from aiomysql.sa import create_engine

from db import sa_connection


def create_app(**config_overrides):
    app = Quart(__name__)

    # Load config
    app.config.from_pyfile("settings.py")

    # apply overrides for tests
    app.config.update(config_overrides)

    # import blueprints
    from user.views import user_app
    from relationship.views import relationship_app
    from home.views import home_app
    from post.views import post_app

    # register blueprints
    app.register_blueprint(user_app)
    app.register_blueprint(relationship_app)
    app.register_blueprint(home_app)
    app.register_blueprint(post_app)

    @app.before_serving
    async def create_db_conn():
        app.sac = await sa_connection()

    @app.after_serving
    async def close_db_conn():
        await app.sac.close()

    return app
