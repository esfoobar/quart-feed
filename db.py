from aiomysql.sa import create_engine
from quart import current_app
import aiomysql


async def sa_connection(loop):
    engine = await create_engine(
        user=current_app.config["DB_USERNAME"],
        password=current_app.config["DB_PASSWORD"],
        host=current_app.config["DB_HOST"],
        db=current_app.config["DATABASE_NAME"],
        minsize=10,
    )
    conn = await engine.acquire()

    # pool = await aiomysql.create_pool(
    #     host=current_app.config["DB_HOST"],
    #     port=3306,
    #     user=current_app.config["DB_USERNAME"],
    #     password=current_app.config["DB_PASSWORD"],
    #     db=current_app.config["DATABASE_NAME"],
    #     loop=loop,
    # )
    # conn2 = await pool.acquire()
    # breakpoint()

    return conn
