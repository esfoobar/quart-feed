from sqlalchemy import Column, Table, Integer, ForeignKey

from user.models import metadata as UserMetadata

relationship_table = Table(
    "relationship",
    UserMetadata,
    Column("id", Integer, primary_key=True),
    Column("fm_user_id", Integer, ForeignKey("user.id")),
    Column("to_user_id", Integer, ForeignKey("user.id")),
)
