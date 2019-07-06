from aiomysql.sa import create_engine
from quart import current_app


async def sa_connection():
    engine = await create_engine(
        user=current_app.config["DB_USERNAME"],
        password=current_app.config["DB_PASSWORD"],
        host=current_app.config["DB_HOST"],
        db=current_app.config["DATABASE_NAME"],
    )
    conn = await engine.acquire()
    return conn
