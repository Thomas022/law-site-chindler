from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db.models.fields.files import FieldFile
from PIL import Image, UnidentifiedImageError


validate_image_extension = FileExtensionValidator(
    allowed_extensions=("jpg", "jpeg", "png", "webp")
)


def validate_property_image(upload):
    # Existing Cloudinary assets are stored by public_id, which intentionally has
    # no file extension. They were already validated when first uploaded, so an
    # unrelated edit must not try to validate or reopen the remote file.
    if isinstance(upload, FieldFile) and upload._committed:
        return

    validate_image_extension(upload)
    content_type = getattr(upload, "content_type", None)
    if content_type and content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise ValidationError("Envie uma imagem JPG, PNG ou WebP.")
    if upload.size > settings.PROPERTY_IMAGE_MAX_BYTES:
        max_megabytes = settings.PROPERTY_IMAGE_MAX_BYTES // (1024 * 1024)
        raise ValidationError(f"A imagem deve ter no máximo {max_megabytes} MB.")

    position = upload.tell() if hasattr(upload, "tell") else None
    try:
        image = Image.open(upload)
        width, height = image.size
        image.verify()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValidationError("O arquivo enviado não é uma imagem válida.") from exc
    finally:
        if hasattr(upload, "seek"):
            upload.seek(position or 0)

    if width * height > settings.PROPERTY_IMAGE_MAX_PIXELS:
        raise ValidationError("A resolução da imagem é maior que o limite permitido.")
