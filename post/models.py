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
)
from aiomysql.sa.connection import SAConnection
import enum

from settings import IMAGES_URL
from user.models import metadata

post_table = Table(
    "post",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("uid", String(36), index=True, unique=True),
    Column("parent_post_id", Integer, ForeignKey("post.id")),
    Column("body", String(280)),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("created", DateTime(timezone=True), server_default=func.now()),
    Column("updated", DateTime(timezone=True), onupdate=func.now()),
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
)

# usage:
# connection.execute(t.insert(), {"value": MyEnum.two})
