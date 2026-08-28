from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageOps


def optimize_property_image(upload):
    upload.seek(0)
    with Image.open(upload) as source:
        image = ImageOps.exif_transpose(source)
        if image.mode not in ("RGB", "L"):
            background = Image.new("RGB", image.size, "white")
            if "A" in image.getbands():
                background.paste(image, mask=image.getchannel("A"))
            else:
                background.paste(image)
            image = background
        elif image.mode == "L":
            image = image.convert("RGB")

        image.thumbnail(
            (settings.PROPERTY_IMAGE_MAX_WIDTH, settings.PROPERTY_IMAGE_MAX_HEIGHT),
            Image.Resampling.LANCZOS,
        )
        output = BytesIO()
        image.save(output, format="JPEG", quality=92, optimize=True, progressive=True)
        output.seek(0)
        width, height = image.size

    filename = f"{Path(upload.name).stem}.jpg"
    content = ContentFile(output.read(), name=filename)
    return content, {
        "width": width,
        "height": height,
        "file_size": content.size,
        "image_format": "JPEG",
    }
