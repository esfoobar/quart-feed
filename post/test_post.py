import pytest
from quart import current_app, session
from sqlalchemy import create_engine, select
import json

from user.models import *
from post.models import *
from relationship.models import *
from db import metadata


def user_dict(username):
    return dict(username=username, password="test123")


@pytest.fixture(scope="module")
def create_all(create_db):
    engine = create_engine(create_db["DB_URI"] + "/" + create_db["DATABASE_NAME"])
    metadata.bind = engine
    metadata.create_all()


@pytest.mark.asyncio
async def test_post_message(create_test_client, create_all, create_test_app):
    response = await create_test_client.post(
        "/register",
        form=user_dict("testuser1"),
    )
    response = await create_test_client.post(
        "/login",
        form=user_dict("testuser1"),
    )

    # post a message
    response = await create_test_client.post(
        "/post",
        data=json.dumps({"post": "Test Post"}),
        headers={"Content-Type": "application/json"},
    )
    response_json = await response.get_json()
    assert response_json.get("result") == "ok"

    # check that the post was recorded
    async with create_test_app.app_context():
        conn = current_app.dbc
        post_query = select([post_table.c.body])
        result_row = await conn.fetch_one(query=post_query)
        body = result_row[post_table.c.body]
        assert body == "Test Post"


@pytest.mark.asyncio
async def test_post_seen_by_followers(create_test_client, create_all, create_test_app):
    # register user2 and user3
    await create_test_client.post(
        "/register",
        form=user_dict("testuser2"),
    )
    await create_test_client.post(
        "/register",
        form=user_dict("testuser3"),
    )
    await create_test_client.post(
        "/login",
        form=user_dict("testuser2"),
    )

    # make user2 follow user1
    await create_test_client.get("/add_friend/testuser1")

    # login as user1 and post something
    await create_test_client.get(
        "/logout",
    )
    await create_test_client.post(
        "/login",
        form=user_dict("testuser1"),
    )

    # post a message
    await create_test_client.post(
        "/post",
        data=json.dumps({"post": "Test Post for testuser2"}),
        headers={"Content-Type": "application/json"},
    )

    # login as user2 and see if we see user1's post
    await create_test_client.get(
        "/logout",
    )
    await create_test_client.post(
        "/login",
        form=user_dict("testuser2"),
    )
    response = await create_test_client.get("/")
    body = await response.get_data()
    assert "Test Post for testuser2" in str(body)

    # login as user3 and check we don't see user1's post
    await create_test_client.get(
        "/logout",
    )
    await create_test_client.post(
        "/login",
        form=user_dict("testuser3"),
    )
    response = await create_test_client.get("/")
    body = await response.get_data()
    assert "Test Post for testuser2" not in str(body)


@pytest.mark.asyncio
async def test_comment_and_likes_seen_by_post_followers(
    create_test_client, create_all, create_test_app
):
    # make user3 follow user2
    await create_test_client.post(
        "/login",
        form=user_dict("testuser3"),
    )
    await create_test_client.get("/add_friend/testuser2")

    # make user1 follow user2
    await create_test_client.get(
        "/logout",
    )
    await create_test_client.post(
        "/login",
        form=user_dict("testuser1"),
    )
    await create_test_client.get("/add_friend/testuser2")

    # login as user2 and post something
    await create_test_client.get(
        "/logout",
    )
    await create_test_client.post(
        "/login",
        form=user_dict("testuser2"),
    )

    await create_test_client.post(
        "/post",
        data=json.dumps({"post": "Test Post for testuser1 and testuser3"}),
        headers={"Content-Type": "application/json"},
    )

    # get postuid for last post
    async with create_test_app.app_context():
        conn = current_app.dbc
        post_query = select([post_table.c.uid]).order_by(desc(post_table.c.id)).limit(1)
        result_row = await conn.fetch_one(query=post_query)
        post_uid = result_row[post_table.c.uid]

    # user3 posts a comment
    await create_test_client.get(
        "/logout",
    )
    await create_test_client.post(
        "/login",
        form=user_dict("testuser3"),
    )
    await create_test_client.post(
        "/comment",
        data=json.dumps(
            {
                "post_uid": post_uid,
                "comment": "Test Comment for testuser1 and testuser3",
            }
        ),
        headers={"Content-Type": "application/json"},
    )

    # user1 should see the comment from user2
    await create_test_client.get(
        "/logout",
    )
    await create_test_client.post(
        "/login",
        form=user_dict("testuser1"),
    )
    response = await create_test_client.get("/")
    body = await response.get_data()
    assert "Test Comment for testuser1 and testuser3" in str(body)

    # user1 likes user2's post
    await create_test_client.post(
        "/like",
        data=json.dumps(
            {
                "post_uid": post_uid,
            }
        ),
        headers={"Content-Type": "application/json"},
    )

    # check user3 sees user1's like
    await create_test_client.get(
        "/logout",
    )
    await create_test_client.post(
        "/login",
        form=user_dict("testuser3"),
    )
    response = await create_test_client.get("/")
    body = await response.get_data()

    # only one like, so if this element is present
    # it means user3 sees user's 1 like
    assert "span-likes-list-item" in str(body)
