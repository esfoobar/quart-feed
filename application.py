from quart import Quart

from db import db_connection


def create_app(**config_overrides):
    app = Quart(__name__)
    app.config["SQLALCHEMY_POOL_SIZE"] = 20

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
        database = await db_connection()
        await database.connect()
        app.dbc = database

    @app.after_serving
    async def close_db_conn():
        await app.dbc.disconnect()

    return app
