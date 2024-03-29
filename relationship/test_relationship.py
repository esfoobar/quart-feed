import pytest
from quart import current_app, session
from sqlalchemy import create_engine, select

from db import metadata
from user.models import *
from relationship.models import *


def user_dict(username):
    return dict(username=username, password="test123")


@pytest.fixture(scope="module")
def create_all(create_db):
    engine = create_engine(create_db["DB_URI"] + "/" + create_db["DATABASE_NAME"])
    metadata.bind = engine
    metadata.create_all()


@pytest.mark.asyncio
async def test_succesful_follow(create_test_client, create_all, create_test_app):
    # create users
    await create_test_client.post("/register", form=user_dict("user1"))
    await create_test_client.post("/register", form=user_dict("user2"))

    # login as user1
    response = await create_test_client.post("/login", form=user_dict("user1"))

    # visit his profile
    response = await create_test_client.get("/user/user2")
    body = await response.get_data()
    assert "@user2" in str(body)

    # Follow user2
    response = await create_test_client.get("/add_friend/user2")
    body = await response.get_data()

    # visit the profile again to get flashed messages
    # since the redirect to referrer is empty since we
    # hit the follow user link directly
    response = await create_test_client.get("/user/user2")
    body = await response.get_data()
    assert "Followed user2" in str(body)
