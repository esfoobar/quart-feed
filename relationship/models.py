from sqlalchemy import Column, Table, Integer, ForeignKey, select
from typing import TYPE_CHECKING, List

from user.models import metadata, user_table

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
    stmt = relationship_table.select().where(
        (relationship_table.c.fm_user_id == fm_user_id)
        & (relationship_table.c.to_user_id == to_user_id)
    )
    result = await conn.execute(stmt)
    record = await result.fetchone()
    return record


async def get_user_followers(conn: "SAConnection", to_user_id: int) -> List["RowProxy"]:
    followers_query = select([user_table]).where(
        (relationship_table.c.fm_user_id == user_table.c.id)
        & (relationship_table.c.to_user_id == to_user_id)
    )
    result = await conn.execute(followers_query)

    followers: list = []
    for row in await result.fetchall():
        followers.append(row)

    return followers

