import pytest
from quart import current_app, session
from sqlalchemy import create_engine, select

from user.models import *
from post.models import *
from db import metadata


def user_dict():
    return dict(username="testuser1", password="test123")


@pytest.fixture(scope="module")
def create_all(create_db):
    engine = create_engine(create_db["DB_URI"] + "/" + create_db["DATABASE_NAME"])
    metadata.bind = engine
    metadata.create_all()


@pytest.mark.asyncio
async def test_post_message(create_test_client, create_all, create_test_app):
    response = await create_test_client.post(
        "/register", form=user_dict(), follow_redirects=True
    )
    response = await create_test_client.post(
        "/login", form=user_dict(), follow_redirects=True
    )
    body = await response.get_data()
    assert "@testuser" in str(body)
