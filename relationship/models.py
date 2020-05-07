from sqlalchemy import Column, Table, Integer, ForeignKey

from user.models import metadata as UserMetadata

relationship_table = Table(
    "relationship",
    UserMetadata,
    Column("id", Integer, primary_key=True),
    Column("fm_user_id", Integer, ForeignKey("user.id")),
    Column("to_user_id", Integer, ForeignKey("user.id")),
)


async def existing_relationship(conn, fm_user_id, to_user_id):
    stmt = relationship_table.select().where(
        (relationship_table.c.fm_user_id == fm_user_id)
        & (relationship_table.c.to_user_id == to_user_id)
    )
    result = await conn.execute(stmt)
    return await result.fetchone()
