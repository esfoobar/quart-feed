from sqlalchemy import (
    Column,
    Table,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
    Enum,
    func,
    select,
    desc,
)
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiomysql.sa.connection import SAConnection

from settings import IMAGES_URL
from user.models import metadata, user_table

post_table = Table(
    "post",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("uid", String(36), index=True, unique=True),
    Column("parent_post_id", Integer, ForeignKey("post.id")),
    Column("body", String(280)),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("created", DateTime(timezone=True), server_default=func.now()),
    Column(
        "updated",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    ),
)

like_table = Table(
    "like",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("parent_post_id", Integer, ForeignKey("post.id")),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("created", DateTime(timezone=True), server_default=func.now()),
)


class ActionType(enum.Enum):
    new_post = 1
    new_comment = 2
    new_like = 3
    delete_post = 4
    delete_comment = 5
    delete_like = 6
    update_post = 7
    update_comment = 8


feed_table = Table(
    "feed",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("post_id", Integer, ForeignKey("post.id")),
    Column("action", Enum(ActionType)),
    Column("fm_user_id", Integer, ForeignKey("user.id")),
    Column("to_user_id", Integer, ForeignKey("user.id")),
    Column("created", DateTime(timezone=True), server_default=func.now()),
    Column(
        "updated",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    ),
)


async def get_latest_posts(
    conn: "SAConnection", user_id: int, num_posts: int = 10, from_post_id: int = 0
):
    # get the last 10 posts in feed in reverse order and
    # pass to the context the last id as cursor_id
    latest_posts_query = (
        select(
            [
                post_table.c.id,
                post_table.c.uid,
                post_table.c.body,
                post_table.c.updated,
                user_table.c.username,
                user_table.c.id,
                user_table.c.image,
            ]
        )
        .where(
            (feed_table.c.post_id == post_table.c.id)
            & (feed_table.c.to_user_id == user_id)
            & (feed_table.c.fm_user_id == user_table.c.id)
            & (feed_table.c.action == ActionType.new_post)
        )
        .order_by(desc(feed_table.c.updated))
        .limit(num_posts)
        .offset(0)
        .apply_labels()
    )

    if from_post_id > 0:
        latest_posts_query.where(feed_table.c.post_id > from_post_id)

    import pdb

    pdb.set_trace()
    result = await conn.execute(latest_posts_query)
    fetch_all = await result.fetchall()
    return fetch_all
