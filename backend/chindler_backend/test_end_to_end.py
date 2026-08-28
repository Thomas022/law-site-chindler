from datetime import timedelta
from decimal import Decimal
from io import BytesIO, StringIO
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from leads.models import Lead
from properties.models import Property, PropertyChange, PropertyImage
from properties.services import change_property_status


def property_photo():
    content = BytesIO()
    Image.new("RGB", (800, 600), "#b89b63").save(content, format="JPEG")
    return SimpleUploadedFile("imovel.jpg", content.getvalue(), content_type="image/jpeg")


class CompletePropertyJourneyTests(TestCase):
    def setUp(self):
        self.media_directory = TemporaryDirectory()
        self.media_override = override_settings(MEDIA_ROOT=self.media_directory.name)
        self.media_override.enable()
        self.user = get_user_model().objects.create_superuser(
            username="journey-admin",
            email="journey@example.com",
            password="Uma-Senha-Segura-123",
        )

    def tearDown(self):
        self.media_override.disable()
        self.media_directory.cleanup()

    def test_complete_property_and_interest_journey(self):
        property_item = Property.objects.create(
            title="Apartamento do teste completo",
            description="Imóvel criado para validar toda a jornada pública.",
            purpose=Property.Purpose.SALE,
            property_type=Property.PropertyType.APARTMENT,
            price=Decimal("1250000.00"),
            total_area=Decimal("105.00"),
            bedrooms=3,
            suites=1,
            bathrooms=2,
            parking_spaces=1,
            street="Rua do Teste",
            number="100",
            neighborhood="Botafogo",
            city="Rio de Janeiro",
            created_by=self.user,
            updated_by=self.user,
        )
        image = PropertyImage(
            property=property_item,
            image=property_photo(),
            alt_text="Sala do apartamento",
            order=0,
            is_cover=True,
        )
        image.full_clean()
        image.save()

        change_property_status(property_item, Property.Status.PUBLISHED, self.user)
        property_item.refresh_from_db()
        self.assertEqual(property_item.status, Property.Status.PUBLISHED)
        self.assertTrue(
            PropertyChange.objects.filter(
                property=property_item,
                action=PropertyChange.Action.STATUS_CHANGED,
            ).exists()
        )

        listing = self.client.get(
            reverse("property-list"),
            {"purpose": "sale", "neighborhood": "Botafogo", "search": "completo"},
        )
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.json()["count"], 1)
        self.assertEqual(listing.json()["results"][0]["id"], str(property_item.public_id))

        detail = self.client.get(
            reverse("property-detail", kwargs={"property_id": property_item.public_id})
        )
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["images"][0]["alt_text"], "Sala do apartamento")
        self.assertNotIn("exact_latitude", detail.json())

        interest = self.client.post(
            reverse("property-interest", kwargs={"property_id": property_item.public_id}),
            data={
                "name": "Cliente da Jornada",
                "phone": "(21) 99999-1111",
                "email": "jornada@example.com",
                "message": "Desejo receber informações e agendar uma visita.",
                "consent": True,
                "website": "",
            },
            content_type="application/json",
        )
        self.assertEqual(interest.status_code, 201)
        lead = Lead.objects.get(property=property_item)
        self.assertEqual(lead.status, Lead.Status.NEW)
        self.assertEqual(lead.property_title, property_item.title)

        Lead.objects.filter(pk=lead.pk).update(
            created_at=timezone.now() - timedelta(days=731)
        )
        call_command("anonymize_expired_leads", stdout=StringIO())
        lead.refresh_from_db()
        self.assertIsNotNone(lead.anonymized_at)
        self.assertEqual(lead.name, "Dados anonimizados")
        self.assertEqual(lead.phone, "")

