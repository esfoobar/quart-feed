from wand.image import Image
import os
import uuid

from settings import UPLOAD_FOLDER

# file = location of raw file
# content_type = app name (i.e. user, post, etc.); these need to be existing folders
#                on upload folder
# content_id = the id related to the image (user.id, post.id)
# size = preset sizes
def thumbnail_process(
    file: str,
    content_type: str,
    content_id: str,
    sizes: list = [("sm", 50), ("lg", 75), ("xlg", 200)],
) -> str:
    image_id = str(uuid.uuid4())
    filename_template = content_id + ".%s.%s.png"

    # original
    with Image(filename=file) as img:
        crop_center(img)
        img.format = "png"
        img.save(
            filename=os.path.join(
                UPLOAD_FOLDER, content_type, filename_template % (image_id, "raw")
            )
        )

    # sizes
    for (name, size) in sizes:
        with Image(filename=file) as img:
            crop_center(img)
            img.sample(size, size)
            img.format = "png"
            img.save(
                filename=os.path.join(
                    UPLOAD_FOLDER, content_type, filename_template % (image_id, name)
                )
            )

    os.remove(file)

    return image_id


def crop_center(image: Image) -> None:
    dst_landscape = 1 > image.width / image.height
    wh = image.width if dst_landscape else image.height
    image.crop(
        left=int((image.width - wh) / 2),
        top=int((image.height - wh) / 2),
        width=int(wh),
        height=int(wh),
    )
