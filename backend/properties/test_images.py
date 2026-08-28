from decimal import Decimal
from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from chindler_backend.storage import CloudinaryMediaStorage

from .models import Property, PropertyImage


def make_uploaded_image(name="fachada.png", size=(3200, 2000), image_format="PNG"):
    content = BytesIO()
    Image.new("RGB", size, "#b89b63").save(content, format=image_format)
    content.seek(0)
    content_type = "image/png" if image_format == "PNG" else "image/jpeg"
    return SimpleUploadedFile(name, content.read(), content_type=content_type)


class LocalImageStorageTests(TestCase):
    def setUp(self):
        self.media_directory = TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_directory.name)
        self.settings_override.enable()
        self.user = get_user_model().objects.create_user(
            username="image-editor", password="Uma-Senha-Segura-123"
        )
        self.property_item = Property.objects.create(
            title="Imóvel para testar imagens",
            description="Cadastro usado pelos testes de upload.",
            purpose=Property.Purpose.SALE,
            property_type=Property.PropertyType.APARTMENT,
            price=Decimal("1000000.00"),
            total_area=Decimal("100.00"),
            street="Rua de Teste",
            number="10",
            neighborhood="Centro",
            city="Rio de Janeiro",
            created_by=self.user,
            updated_by=self.user,
        )

    def tearDown(self):
        self.settings_override.disable()
        self.media_directory.cleanup()

    def test_upload_is_resized_and_converted_to_optimized_jpeg(self):
        image = PropertyImage(
            property=self.property_item,
            image=make_uploaded_image(),
            order=0,
            is_cover=True,
        )
        image.full_clean()
        image.save()

        self.assertEqual(image.image_format, "JPEG")
        self.assertEqual((image.width, image.height), (2400, 1500))
        self.assertLess(image.file_size, 15 * 1024 * 1024)
        self.assertTrue(image.image.name.endswith(".jpg"))
        self.assertTrue(image.image.storage.exists(image.image.name))

    def test_unsupported_format_is_rejected(self):
        image = PropertyImage(
            property=self.property_item,
            image=make_uploaded_image(name="fachada.gif", image_format="PNG"),
            order=0,
        )

        with self.assertRaises(ValidationError):
            image.full_clean()

    @override_settings(PROPERTY_IMAGE_MAX_BYTES=10)
    def test_file_larger_than_limit_is_rejected(self):
        image = PropertyImage(
            property=self.property_item,
            image=make_uploaded_image(size=(100, 100)),
            order=0,
        )

        with self.assertRaises(ValidationError):
            image.full_clean()

    def test_file_is_removed_after_image_record_is_deleted(self):
        image = PropertyImage(
            property=self.property_item,
            image=make_uploaded_image(size=(300, 200)),
            order=0,
            is_cover=True,
        )
        image.full_clean()
        image.save()
        image_name = image.image.name

        with self.captureOnCommitCallbacks(execute=True):
            image.delete()

        self.assertFalse(image.image.storage.exists(image_name))

    def test_existing_cloudinary_public_id_does_not_require_a_new_upload(self):
        image = PropertyImage.objects.create(
            property=self.property_item,
            image="properties/public-id/photo-without-extension",
            order=0,
            is_cover=True,
        )

        image.refresh_from_db()
        image.alt_text = "Nova descrição da imagem"
        image.full_clean()

        self.assertEqual(image.image.name, "properties/public-id/photo-without-extension")


class CloudinaryStorageTests(TestCase):
    @patch("chindler_backend.storage.cloudinary.uploader.upload")
    def test_upload_returns_cloudinary_public_id(self, upload):
        upload.return_value = {"public_id": "properties/public-id/photo-123"}
        storage = CloudinaryMediaStorage()

        saved_name = storage.save(
            "properties/public-id/photo.jpg", ContentFile(b"image-content")
        )

        self.assertEqual(saved_name, "properties/public-id/photo-123")
        upload.assert_called_once()

    @patch("chindler_backend.storage.cloudinary.uploader.destroy")
    def test_delete_invalidates_cloudinary_asset(self, destroy):
        storage = CloudinaryMediaStorage()

        storage.delete("properties/public-id/photo-123")

        destroy.assert_called_once_with(
            "properties/public-id/photo-123", resource_type="image", invalidate=True
        )
