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
from sqlalchemy.orm import relationship
from db import metadata
import enum
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from aiomysql.sa.connection import SAConnection

from settings import IMAGES_URL
from user.models import user_table

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
    Column("uid", String(36), index=True, unique=True),
    Column("parent_post_id", Integer, ForeignKey("post.id")),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("created", DateTime(timezone=True), server_default=func.now()),
)


class ActionType(enum.Enum):
    new_post = 1
    new_comment = 2
    new_like = 3


feed_table = Table(
    "feed",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("uid", String(36), index=True, unique=True),
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
    conn: "SAConnection",
    user_id: int,
    num_posts: int = 10,
    from_post_id: int = 0,
):

    # if from_post_id > 0 then we want to get all feed items
    if from_post_id > 0:
        latest_posts_query = (
            select(
                [
                    feed_table.c.id,
                    feed_table.c.uid,
                    post_table.c.id,
                    post_table.c.uid,
                    post_table.c.parent_post_id,
                    post_table.c.body,
                    feed_table.c.action,
                    feed_table.c.updated,
                    user_table.c.username,
                    user_table.c.id,
                    user_table.c.image,
                ]
            )
            .where(
                (feed_table.c.id > from_post_id)
                & (feed_table.c.post_id == post_table.c.id)
                & (feed_table.c.to_user_id == user_id)
                & (feed_table.c.fm_user_id == user_table.c.id)
            )
            .order_by(desc(feed_table.c.updated))
            .limit(num_posts)
            .offset(0)
            .apply_labels()
        )

    # otherwise this is the initial post query, so just get posts only
    # not comments and likes
    else:
        latest_posts_query = (
            select(
                [
                    feed_table.c.id,
                    feed_table.c.uid,
                    post_table.c.id,
                    post_table.c.uid,
                    post_table.c.parent_post_id,
                    post_table.c.body,
                    feed_table.c.action,
                    feed_table.c.updated,
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

    fetch_all = await conn.fetch_all(query=latest_posts_query)
    return fetch_all


async def get_post_comments(
    conn: "SAConnection",
    post_uid: str,
):

    parent_post_query = (
        select(
            [
                post_table.c.id,
            ]
        )
        .where((post_table.c.uid == post_uid))
        .apply_labels()
    )
    fetch_one = await conn.fetch_one(query=parent_post_query)
    parent_post_id = fetch_one["post_id"]

    post_comments_query = (
        select(
            [
                post_table.c.uid,
                post_table.c.body,
                user_table.c.username,
            ]
        )
        .where(
            (post_table.c.parent_post_id == parent_post_id)
            & (post_table.c.user_id == user_table.c.id)
        )
        .order_by((post_table.c.updated))
        .apply_labels()
    )
    fetch_all = await conn.fetch_all(query=post_comments_query)
    return fetch_all


async def get_comment_parent_uid(
    conn: "SAConnection",
    post_id: int,
):

    parent_post_query = (
        select(
            [
                post_table.c.parent_post_id,
            ]
        )
        .where((post_table.c.id == post_id))
        .apply_labels()
    )
    fetch_one = await conn.fetch_one(query=parent_post_query)
    parent_post_id = fetch_one["post_parent_post_id"]

    post_query = (
        select(
            [
                post_table.c.uid,
            ]
        )
        .where((post_table.c.id == parent_post_id))
        .apply_labels()
    )
    fetch_one = await conn.fetch_one(query=post_query)
    parent_post_uid = fetch_one["post_uid"]

    return parent_post_uid


async def get_post_feed_followers(
    conn: "SAConnection",
    post_id: int,
):

    feed_post_followers_query = (
        select(
            [
                feed_table.c.to_user_id,
            ]
        )
        .where((feed_table.c.post_id == post_id))
        .group_by(feed_table.c.to_user_id)
        .apply_labels()
    )
    fetch_all = await conn.fetch_all(query=feed_post_followers_query)
    return fetch_all


async def get_last_feed_id(
    conn: "SAConnection",
    user_id: int,
):

    last_feed_post_query = (
        select(
            [
                feed_table.c.id,
            ]
        )
        .where((feed_table.c.to_user_id == user_id))
        .order_by(desc(feed_table.c.updated))
        .limit(1)
        .apply_labels()
    )
    fetch_one = await conn.fetch_one(query=last_feed_post_query)
    if fetch_one:
        return fetch_one["feed_id"]
    else:
        return 0
