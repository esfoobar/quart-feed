from sqlalchemy import Column, Table, Integer, ForeignKey, select
from typing import TYPE_CHECKING, List

from user.models import user_table
from db import metadata

if TYPE_CHECKING:
    from aiomysql.sa.connection import SAConnection
    from aiomysql.sa.result import RowProxy

relationship_table = Table(
    "relationship",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("fm_user_id", Integer, ForeignKey("user.id")),
    Column("to_user_id", Integer, ForeignKey("user.id")),
)


async def existing_relationship(
    conn: "SAConnection", fm_user_id: int, to_user_id: int
) -> "RowProxy":
    rel_query = relationship_table.select().where(
        (relationship_table.c.fm_user_id == fm_user_id)
        & (relationship_table.c.to_user_id == to_user_id)
    )
    record = await conn.fetch_one(query=rel_query)
    return record


async def get_user_followers(conn: "SAConnection", to_user_id: int) -> List["RowProxy"]:
    followers_query = select([user_table]).where(
        (relationship_table.c.fm_user_id == user_table.c.id)
        & (relationship_table.c.to_user_id == to_user_id)
    )

    followers: list = []
    async for row in conn.iterate(query=followers_query):
        followers.append(row)

    return followers
