import pytest
import asyncio
import os, sys
from dotenv import load_dotenv
from sqlalchemy import create_engine

# This needs to go above the create_app import
load_dotenv(".quartenv")

from application import create_app

# We need our own module-level event_loop
# since pytest's is a function-level fixture
@pytest.yield_fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
@pytest.fixture(scope="module")
async def create_db(event_loop):
    db_name = os.environ["DATABASE_NAME"] + "_test"
    db_host = os.environ["DB_HOST"]
    db_root_password = os.environ["MYSQL_ROOT_PASSWORD"]
    if db_root_password:
        db_username = "root"
        db_password = db_root_password
    else:
        db_username = os.environ["DB_USERNAME"]
        db_password = os.environ["DB_PASSWORD"]

    db_uri = "mysql+pymysql://%s:%s@%s:3306" % (db_username, db_password, db_host)

    engine = create_engine(db_uri)
    conn = engine.connect()
    conn.execute("CREATE DATABASE " + db_name)
    conn.execute("COMMIT")
    conn.close()

    # TESTING flag disables error catching during request handling,
    # so that you get better error reports when performing test requests
    # against the application.
    yield {
        "SECRET_KEY": "my_secret_key",
        "DB_USERNAME": db_username,
        "DB_PASSWORD": db_password,
        "DB_HOST": db_host,
        "DATABASE_NAME": db_name,
        "DB_URI": db_uri,
        "TESTING": True,
    }

    engine = create_engine(db_uri)
    conn = engine.connect()
    conn.execute("DROP DATABASE " + db_name)
    conn.execute("COMMIT")
    conn.close()


@pytest.fixture(scope="module")
async def create_test_app(create_db):
    app = create_app(**create_db)
    async with app.test_app():
        yield app


@pytest.fixture
def create_test_client(create_test_app):
    return create_test_app.test_client()
