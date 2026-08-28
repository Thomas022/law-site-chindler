from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from properties.models import Property

from .models import Lead


class LeadModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="administrator", password="test-password"
        )
        cls.property_item = Property.objects.create(
            title="Casa no Jardim Botânico",
            description="Casa cercada pelo verde.",
            purpose=Property.Purpose.RENT,
            property_type=Property.PropertyType.HOUSE,
            price=Decimal("12000.00"),
            total_area=Decimal("300.00"),
            street="Rua Jardim Botânico",
            number="500",
            neighborhood="Jardim Botânico",
            city="Rio de Janeiro",
            created_by=cls.user,
            updated_by=cls.user,
        )

    def test_lead_stores_property_snapshot_and_responsible_user(self):
        lead = Lead.objects.create(
            property=self.property_item,
            property_title=self.property_item.title,
            name="Cliente Teste",
            phone="(21) 99999-0000",
            email="cliente@example.com",
            message="Gostaria de agendar uma visita.",
            responsible=self.user,
            consent_version="1.0",
            consent_at=timezone.now(),
        )

        self.assertEqual(lead.status, Lead.Status.NEW)
        self.assertEqual(lead.property_title, "Casa no Jardim Botânico")
        self.assertEqual(lead.responsible, self.user)

    def test_retention_deadline_is_two_years_after_last_interaction(self):
        last_interaction = timezone.now()
        lead = Lead.objects.create(
            property=self.property_item,
            property_title=self.property_item.title,
            name="Cliente Teste",
            phone="(21) 99999-0000",
            email="cliente@example.com",
            message="Tenho interesse.",
            consent_version="1.0",
            consent_at=timezone.now(),
            last_interaction_at=last_interaction,
        )

        self.assertEqual(
            lead.retention_deadline,
            last_interaction + timedelta(days=730),
        )
