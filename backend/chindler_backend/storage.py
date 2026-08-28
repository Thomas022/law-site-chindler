from pathlib import PurePosixPath

import cloudinary
import cloudinary.uploader
from cloudinary import CloudinaryImage
from django.core.files.storage import Storage


class CloudinaryMediaStorage(Storage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cloudinary.config(secure=True)

    def _save(self, name, content):
        path = PurePosixPath(name)
        public_id = str(path.with_suffix(""))
        result = cloudinary.uploader.upload(
            content,
            public_id=public_id,
            resource_type="image",
            overwrite=False,
            unique_filename=True,
            allowed_formats=["jpg", "jpeg", "png", "webp"],
            transformation=[
                {"width": 2400, "height": 1800, "crop": "limit", "quality": "auto:good"}
            ],
        )
        return result["public_id"]

    def delete(self, name):
        if name:
            cloudinary.uploader.destroy(name, resource_type="image", invalidate=True)

    def exists(self, name):
        return False

    def url(self, name):
        return CloudinaryImage(name).build_url(
            secure=True,
            fetch_format="auto",
            quality="auto",
        )

    def transformed_url(self, name, *, width, height, crop="fill"):
        return CloudinaryImage(name).build_url(
            secure=True,
            width=width,
            height=height,
            crop=crop,
            gravity="auto",
            fetch_format="auto",
            quality="auto",
        )
