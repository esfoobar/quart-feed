import pytest
from quart import current_app, session
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
async def test_succesful_registration(create_test_client, create_all, create_test_app):
    response = await create_test_client.post(
        "/register", form=user_dict(), follow_redirects=True
    )
    body = await response.get_data()
    assert "You have been registered" in str(body)

    # check that the user was created on the database itself
    async with create_test_app.app_context():
        conn = current_app.sac
        username_query = select([user_table.c.username])
        result = await conn.execute(username_query)
        result_row = await result.first()
        username = result_row[user_table.c.username]
        assert username == user_dict()["username"]


@pytest.mark.asyncio
async def test_missing_fields_registration(create_test_client, create_all):
    # no fields
    response = await create_test_client.post(
        "/register", form={"username": "", "password": ""}
    )
    body = await response.get_data()
    assert "Please enter username and password" in str(body)

    # missing password
    response = await create_test_client.post(
        "/register", form={"username": "testuser", "password": ""}
    )
    body = await response.get_data()
    assert "Please enter username and password" in str(body)

    # missing username
    response = await create_test_client.post(
        "/register", form={"username": "", "password": "test123"}
    )
    body = await response.get_data()
    assert "Please enter username and password" in str(body)


@pytest.mark.asyncio
async def test_existing_user_registration(create_test_client, create_all):
    # no fields
    response = await create_test_client.post("/register", form=user_dict())
    body = await response.get_data()
    assert "Username already exists" in str(body)


@pytest.mark.asyncio
async def test_succesful_login(create_test_client, create_all, create_test_app):
    response = await create_test_client.post(
        "/login", form=user_dict(), follow_redirects=True
    )
    body = await response.get_data()
    assert "User logged in" in str(body)

    response = await create_test_app.test_client().post(
        "/login", form=user_dict(), follow_redirects=True
    )
    response = await create_test_client.get("/login")
    body = await response.get_data()
    assert "testuser" in str(body)

    # Check that the session is being set
    async with create_test_client.session_transaction() as sess:
        assert sess["user_id"] == 1


@pytest.mark.asyncio
async def test_user_not_found_login(create_test_client, create_all):
    # no fields
    response = await create_test_client.post(
        "/login", form={"username": "testuser2", "password": "test123"}
    )
    body = await response.get_data()
    assert "User not found" in str(body)


@pytest.mark.asyncio
async def test_wrong_password_login(create_test_client, create_all):
    # no fields
    response = await create_test_client.post(
        "/login", form={"username": "testuser", "password": "wrong123"}
    )
    body = await response.get_data()
    assert "User not found" in str(body)
