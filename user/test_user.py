import pytest
from quart import current_app
from sqlalchemy import create_engine, select

from user.models import user_table, metadata as UserMetadata


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
