from databases import Database
from quart import current_app
import sqlalchemy

metadata = sqlalchemy.MetaData()


async def db_connection():
    database = Database(
        f"mysql://{current_app.config['DB_USERNAME']}:{current_app.config['DB_PASSWORD']}@{current_app.config['DB_HOST']}/{current_app.config['DATABASE_NAME']}?min_size=5&max_size=20"
    )

    return database
