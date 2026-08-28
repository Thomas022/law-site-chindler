from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from properties.models import Property

from .models import Lead


class PropertyInterestAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user(
            username="lead-api-editor", password="not-used"
        )
        cls.property = Property.objects.create(
            title="Apartamento publicado",
            description="Imóvel disponível para visita.",
            purpose=Property.Purpose.SALE,
            property_type=Property.PropertyType.APARTMENT,
            status=Property.Status.PUBLISHED,
            price=Decimal("950000.00"),
            total_area=Decimal("90.00"),
            street="Rua das Flores",
            number="10",
            neighborhood="Botafogo",
            city="Rio de Janeiro",
            created_by=user,
            updated_by=user,
        )
        cls.draft = Property.objects.create(
            title="Rascunho",
            description="Ainda indisponível.",
            purpose=Property.Purpose.RENT,
            property_type=Property.PropertyType.HOUSE,
            status=Property.Status.DRAFT,
            price=Decimal("5000.00"),
            total_area=Decimal("120.00"),
            street="Rua Interna",
            number="20",
            neighborhood="Tijuca",
            city="Rio de Janeiro",
            created_by=user,
            updated_by=user,
        )

    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.url = reverse(
            "property-interest", kwargs={"property_id": self.property.public_id}
        )
        self.payload = {
            "name": "Maria da Silva",
            "phone": "(21) 99999-0000",
            "email": "maria@example.com",
            "message": "Gostaria de agendar uma visita ao imóvel.",
            "consent": True,
            "website": "",
        }

    def test_creates_lead_linked_to_published_property(self):
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        lead = Lead.objects.get()
        self.assertEqual(lead.property, self.property)
        self.assertEqual(lead.property_title, self.property.title)
        self.assertEqual(lead.status, Lead.Status.NEW)
        self.assertEqual(lead.consent_version, "1.0")

    def test_rejects_missing_consent_and_invalid_phone(self):
        payload = {**self.payload, "phone": "123", "consent": False}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone", response.data)
        self.assertIn("consent", response.data)
        self.assertFalse(Lead.objects.exists())

    def test_does_not_accept_interest_for_draft_property(self):
        url = reverse("property-interest", kwargs={"property_id": self.draft.public_id})
        response = self.client.post(url, self.payload, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Lead.objects.exists())

    def test_honeypot_silently_discards_bot_submission(self):
        response = self.client.post(
            self.url, {**self.payload, "website": "https://spam.example"}, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertFalse(Lead.objects.exists())

