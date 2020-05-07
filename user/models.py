from sqlalchemy import Column, Table, Integer, String, MetaData

metadata = MetaData()

user_table = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(15), index=True, unique=True),
    Column("password", String(128)),
)


async def get_user_by_username(conn, username):
    stmt = user_table.select().where(user_table.c.username == username)
    result = await conn.execute(stmt)
    return await result.fetchone()
