from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from .models import Lead
from .services import anonymize_lead


class LeadPrivacyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="privacy-admin", password="not-used"
        )

    def create_lead(self, *, days_old=0, last_interaction_at=None):
        lead = Lead.objects.create(
            property=None,
            property_title="Imóvel preservado para histórico",
            name="Pessoa Interessada",
            phone="(21) 99999-0000",
            email="pessoa@example.com",
            message="Mensagem com dados pessoais.",
            responsible=self.user,
            consent_version="1.0",
            consent_at=timezone.now(),
            last_interaction_at=last_interaction_at,
        )
        if days_old:
            Lead.objects.filter(pk=lead.pk).update(
                created_at=timezone.now() - timedelta(days=days_old)
            )
            lead.refresh_from_db()
        return lead

    def test_anonymization_removes_personal_data_and_is_idempotent(self):
        lead = self.create_lead()
        self.assertTrue(anonymize_lead(lead))
        lead.refresh_from_db()
        self.assertEqual(lead.name, "Dados anonimizados")
        self.assertEqual(lead.phone, "")
        self.assertNotIn("pessoa@example.com", lead.email)
        self.assertNotIn("dados pessoais", lead.message)
        self.assertIsNone(lead.responsible)
        self.assertIsNotNone(lead.anonymized_at)
        self.assertFalse(anonymize_lead(lead))

    def test_command_anonymizes_only_expired_leads(self):
        expired = self.create_lead(days_old=731)
        recent = self.create_lead(days_old=10)
        call_command("anonymize_expired_leads", stdout=StringIO())
        expired.refresh_from_db()
        recent.refresh_from_db()
        self.assertIsNotNone(expired.anonymized_at)
        self.assertIsNone(recent.anonymized_at)

    def test_last_interaction_renews_retention_period(self):
        lead = self.create_lead(days_old=900, last_interaction_at=timezone.now())
        call_command("anonymize_expired_leads", stdout=StringIO())
        lead.refresh_from_db()
        self.assertIsNone(lead.anonymized_at)

    def test_dry_run_does_not_change_data(self):
        lead = self.create_lead(days_old=731)
        output = StringIO()
        call_command("anonymize_expired_leads", "--dry-run", stdout=output)
        lead.refresh_from_db()
        self.assertIsNone(lead.anonymized_at)
        self.assertIn("1 interessado(s) seriam anonimizados", output.getvalue())

