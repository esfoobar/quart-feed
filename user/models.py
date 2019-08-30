from sqlalchemy import Column, Table, Integer, String, MetaData

metadata = MetaData()

user_table = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(15), index=True, unique=True),
    Column("password", String(128)),
)
# see
# https://docs.sqlalchemy.org/en/13/core/tutorial.html
