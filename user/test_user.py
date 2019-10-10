import pytest
from quart import current_app
from sqlalchemy import create_engine, select

from user.models import user_table, metadata as UserMetadata


def user_dict():
    return dict(username="testuser", password="test123")


@pytest.fixture(scope="module")
def create_all(create_db):
    print("Creating Models")
    engine = create_engine(create_db["DB_URI"] + "/" + create_db["DATABASE_NAME"])
    UserMetadata.bind = engine
    UserMetadata.create_all()


@pytest.mark.asyncio
async def test_initial_response(create_test_client, create_all):
    response = await create_test_client.get("/register")
    body = await response.get_data()
    assert "Registration" in str(body)


@pytest.mark.asyncio
async def test_succesful_registration(create_test_client, create_all):
    response = await create_test_client.post(
        "/register", form=user_dict(), follow_redirects=True
    )
    body = await response.get_data()
    print(body)
    assert "You have been registered" in str(body)
