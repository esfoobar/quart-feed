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

    image_dict = image_url_from_image_ts(user_dict["id"], user_dict["image"])
    user_dict["image_url_raw"] = image_dict["image_url_raw"]
    user_dict["image_url_xlg"] = image_dict["image_url_xlg"]
    user_dict["image_url_lg"] = image_dict["image_url_lg"]
    user_dict["image_url_sm"] = image_dict["image_url_sm"]

    return user_dict


def image_url_from_image_ts(user_id: int, user_image: str) -> dict:
    # compute the image url
    image_dict:dict = []
    if user_image:
        image_dict[
            "image_url_raw"
        ] = f"{IMAGES_URL}/user/{user_id}.{user_image}.raw.png"
        image_dict[
            "image_url_xlg"
        ] = f"{IMAGES_URL}/user/{user_id}.{user_image]}.xlg.png"
        image_dict[
            "image_url_lg"
        ] = f"{IMAGES_URL}/user/{user_id}.{user_image}.lg.png"
        image_dict[
            "image_url_sm"
        ] = f"{IMAGES_URL}/user/{user_id}.{user_image}.sm.png"
    else:
        image_dict["image_url_raw"] = f"{IMAGES_URL}/user/profile.raw.png"
        image_dict["image_url_xlg"] = f"{IMAGES_URL}/user/profile.xlg.png"
        image_dict["image_url_lg"] = f"{IMAGES_URL}/user/profile.lg.png"
        image_dict["image_url_sm"] = f"{IMAGES_URL}/user/profile.sm.png"
    return image_dict
