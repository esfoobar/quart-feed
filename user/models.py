from sqlalchemy import Column, Table, Integer, String, MetaData
from aiomysql.sa.connection import SAConnection

from settings import IMAGES_URL

metadata = MetaData()

user_table = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(15), index=True, unique=True),
    Column("password", String(128)),
    Column("image", String(45), nullable=True),
)


async def get_user_by_username(conn: SAConnection, username: str) -> dict:
    stmt = user_table.select().where(user_table.c.username == username)
    result = await conn.execute(stmt)
    user_row = await result.fetchone()

    if user_row:
        user_dict = dict(user_row)
    else:
        return {}

    # compute the image url
    if user_dict["image"]:
        user_dict[
            "image_url_raw"
        ] = f"{IMAGES_URL}/user/{user_dict['id']}.{user_dict['image']}.raw.png"
        user_dict[
            "image_url_xlg"
        ] = f"{IMAGES_URL}/user/{user_dict['id']}.{user_dict['image']}.xlg.png"
        user_dict[
            "image_url_lg"
        ] = f"{IMAGES_URL}/user/{user_dict['id']}.{user_dict['image']}.lg.png"
        user_dict[
            "image_url_sm"
        ] = f"{IMAGES_URL}/user/{user_dict['id']}.{user_dict['image']}.sm.png"
    else:
        user_dict["image_url_raw"] = f"{IMAGES_URL}/user/profile.raw.png"
        user_dict["image_url_xlg"] = f"{IMAGES_URL}/user/profile.xlg.png"
        user_dict["image_url_lg"] = f"{IMAGES_URL}/user/profile.lg.png"
        user_dict["image_url_sm"] = f"{IMAGES_URL}/user/profile.sm.png"
    return user_dict
