from datetime import timedelta
from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from properties.models import Property

from .admin import LeadAdmin, LeadAdminForm, NextActionFilter
from .models import Lead, LeadInteraction, LeadTask


class LeadCrmAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            username="crm-admin", email="crm@example.com", password="test-password-123"
        )
        cls.property_item = Property.objects.create(
            title="Apartamento em Copacabana",
            description="Imóvel de teste.",
            purpose=Property.Purpose.SALE,
            property_type=Property.PropertyType.APARTMENT,
            price=Decimal("950000.00"),
            total_area=Decimal("90.00"),
            street="Rua Barata Ribeiro",
            number="100",
            neighborhood="Copacabana",
            city="Rio de Janeiro",
            created_by=cls.user,
            updated_by=cls.user,
        )

    def setUp(self):
        self.lead = Lead.objects.create(
            property=self.property_item,
            property_title=self.property_item.title,
            name="Mariana Costa",
            phone="(21) 99999-0000",
            email="mariana@example.com",
            message="Gostaria de visitar.",
            consent_version="1.0",
            consent_at=timezone.now(),
        )
        self.admin = LeadAdmin(Lead, admin.site)
        self.factory = RequestFactory()

    def test_models_store_history_and_multiple_tasks(self):
        interaction = LeadInteraction.objects.create(
            lead=self.lead,
            kind=LeadInteraction.Kind.CALL,
            description="Contato realizado.",
            outcome="Visita solicitada.",
            created_by=self.user,
        )
        first = LeadTask.objects.create(
            lead=self.lead,
            kind=LeadTask.Kind.VISIT,
            due_at=timezone.now() + timedelta(days=1),
            responsible=self.user,
            created_by=self.user,
        )
        second = LeadTask.objects.create(
            lead=self.lead,
            kind=LeadTask.Kind.FOLLOW_UP,
            due_at=timezone.now() + timedelta(days=2),
            responsible=self.user,
            created_by=self.user,
        )

        self.assertEqual(self.lead.interactions.get(), interaction)
        self.assertEqual(list(self.lead.tasks.all()), [first, second])

    def test_discard_requires_reason(self):
        form = LeadAdminForm(
            data={
                "property": self.property_item.pk,
                "property_title": self.property_item.title,
                "name": self.lead.name,
                "phone": self.lead.phone,
                "email": self.lead.email,
                "message": self.lead.message,
                "status": Lead.Status.DISCARDED,
                "priority": Lead.Priority.NORMAL,
                "source": Lead.Source.WEBSITE,
                "consent_version": "1.0",
                "consent_at": timezone.now(),
            },
            instance=self.lead,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("discard_reason", form.errors)

    def test_admin_records_status_and_assignment_history(self):
        request = self.factory.post("/admin/leads/lead/")
        request.user = self.user
        self.lead.status = Lead.Status.IN_PROGRESS
        self.lead.responsible = self.user

        self.admin.save_model(request, self.lead, form=None, change=True)

        kinds = set(self.lead.interactions.values_list("kind", flat=True))
        self.assertEqual(
            kinds,
            {LeadInteraction.Kind.STATUS_CHANGE, LeadInteraction.Kind.ASSIGNMENT},
        )
        self.lead.refresh_from_db()
        self.assertIsNotNone(self.lead.last_interaction_at)

    def test_changelist_shows_operational_indicators(self):
        LeadTask.objects.create(
            lead=self.lead,
            kind=LeadTask.Kind.CALL,
            due_at=timezone.now() - timedelta(hours=1),
            responsible=self.user,
            created_by=self.user,
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("admin:leads_lead_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Novos")
        self.assertContains(response, "Visitas agendadas")
        self.assertContains(response, "Atrasados")
        self.assertContains(response, "Ligação")
        self.assertContains(response, "lead-status--new")

    def test_individual_page_contains_tasks_history_and_contact_actions(self):
        LeadTask.objects.create(
            lead=self.lead,
            kind=LeadTask.Kind.CALL,
            due_at=timezone.now() + timedelta(hours=2),
            notes="Retornar o contato.",
            created_by=self.user,
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("admin:leads_lead_change", args=[self.lead.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Próximas ações e tarefas")
        self.assertContains(response, "Interações e histórico")
        self.assertContains(response, "Situação atual")
        self.assertContains(response, "WhatsApp")
        self.assertContains(response, "Retornar o contato")

    def test_manual_lead_can_be_created_with_required_minimum(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("admin:leads_lead_add"),
            {
                "name": "João Manual",
                "email": "joao@example.com",
                "message": "Contato recebido diretamente no escritório.",
                "phone": "",
                "property": "",
                "responsible": "",
                "priority": Lead.Priority.NORMAL,
                "tasks-TOTAL_FORMS": "1",
                "tasks-INITIAL_FORMS": "0",
                "tasks-MIN_NUM_FORMS": "0",
                "tasks-MAX_NUM_FORMS": "1000",
                "tasks-0-kind": "",
                "tasks-0-due_at_0": "",
                "tasks-0-due_at_1": "",
                "tasks-0-responsible": "",
                "tasks-0-notes": "",
                "tasks-0-status": LeadTask.Status.PENDING,
                "interactions-TOTAL_FORMS": "1",
                "interactions-INITIAL_FORMS": "0",
                "interactions-MIN_NUM_FORMS": "0",
                "interactions-MAX_NUM_FORMS": "1000",
                "interactions-0-kind": LeadInteraction.Kind.NOTE,
                "interactions-0-description": "",
                "interactions-0-outcome": "",
                "interactions-0-occurred_at_0": "",
                "interactions-0-occurred_at_1": "",
                "_save": "Salvar",
            },
        )

        self.assertEqual(response.status_code, 302)
        manual = Lead.objects.get(email="joao@example.com")
        self.assertEqual(manual.source, Lead.Source.MANUAL)
        self.assertEqual(manual.status, Lead.Status.NEW)
        self.assertEqual(manual.property_title, "Interesse geral")
        self.assertEqual(manual.phone, "")
        self.assertIsNone(manual.property)
        self.assertIsNone(manual.consent_at)
        self.assertEqual(manual.responsible, self.user)

    def test_discarded_leads_are_hidden_from_dashboard_but_available_by_filter(self):
        self.lead.status = Lead.Status.DISCARDED
        self.lead.discard_reason = "Sem interesse no momento."
        self.lead.save(update_fields=("status", "discard_reason"))
        self.client.force_login(self.user)

        dashboard = self.client.get(reverse("admin:leads_lead_changelist"))
        discarded = self.client.get(
            reverse("admin:leads_lead_changelist"),
            {"status__exact": Lead.Status.DISCARDED},
        )

        self.assertNotContains(dashboard, self.lead.name)
        self.assertContains(discarded, self.lead.name)
