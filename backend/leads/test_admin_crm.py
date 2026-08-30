from datetime import timedelta
from decimal import Decimal

from django.contrib import admin
from django.contrib.admin.models import CHANGE, DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
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

    def test_current_status_section_does_not_show_discard_reason(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("admin:leads_lead_change", args=[self.lead.pk])
        )

        self.assertNotContains(response, "Motivo do descarte")

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
        self.assertContains(response, "Concluídos")
        self.assertContains(response, "<h1>Interessados</h1>", html=True)
        self.assertContains(response, "?status__exact=completed")
        self.assertContains(response, "Ligação")
        self.assertContains(response, "lead-status--new")
        self.assertContains(response, "Pesquisar por nome, telefone, e-mail ou imóvel")
        self.assertContains(response, 'name="q"')
        self.assertContains(response, "Filtros dos interessados")
        self.assertContains(response, "Filtrar interessados")
        self.assertContains(response, "Abrir")
        self.assertIsNone(self.admin.date_hierarchy)
        rendered = response.content.decode()
        self.assertLess(
            rendered.index('class="paginator"'),
            rendered.index('class="lead-filter-panel lead-filter-panel--below"'),
        )

    def test_completed_dashboard_metric_counts_and_filters_completed_leads(self):
        self.lead.status = Lead.Status.COMPLETED
        self.lead.completed_at = timezone.now()
        self.lead.save(update_fields=("status", "completed_at"))
        Lead.objects.create(
            property_title="Interesse ainda em atendimento",
            name="Contato em andamento",
            email="andamento@example.com",
            message="Ainda não concluído.",
            status=Lead.Status.IN_PROGRESS,
        )
        self.client.force_login(self.user)

        dashboard = self.client.get(reverse("admin:leads_lead_changelist"))
        completed = self.client.get(
            reverse("admin:leads_lead_changelist"),
            {"status__exact": Lead.Status.COMPLETED},
        )

        self.assertEqual(dashboard.context["lead_counts"]["completed"], 1)
        self.assertContains(completed, self.lead.name)
        self.assertNotContains(completed, "Contato em andamento")

    def test_admin_dashboard_shows_only_current_users_three_latest_actions(self):
        content_type = ContentType.objects.get_for_model(Lead)
        other_user = get_user_model().objects.create_superuser(
            username="other-admin",
            email="other@example.com",
            password="other-password-123",
        )
        for index in range(1, 5):
            LogEntry.objects.create(
                user=self.user,
                content_type=content_type,
                object_id=str(self.lead.pk),
                object_repr=f"Minha ação {index}",
                action_flag=CHANGE,
                change_message="Teste",
            )
        LogEntry.objects.create(
            user=other_user,
            content_type=content_type,
            object_id=str(self.lead.pk),
            object_repr="Ação de outro usuário",
            action_flag=CHANGE,
            change_message="Teste",
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("admin:index"))

        self.assertNotContains(response, "Minha ação 1")
        self.assertContains(response, "Minha ação 2")
        self.assertContains(response, "Minha ação 3")
        self.assertContains(response, "Minha ação 4")
        self.assertNotContains(response, "Ação de outro usuário")

    def test_dashboard_counts_each_lead_once_when_it_has_multiple_tasks(self):
        self.lead.status = Lead.Status.IN_PROGRESS
        self.lead.save(update_fields=("status",))
        LeadTask.objects.create(
            lead=self.lead,
            kind=LeadTask.Kind.CALL,
            due_at=timezone.now() - timedelta(hours=1),
            status=LeadTask.Status.COMPLETED,
            completed_at=timezone.now(),
            responsible=self.user,
            created_by=self.user,
        )
        LeadTask.objects.create(
            lead=self.lead,
            kind=LeadTask.Kind.FOLLOW_UP,
            due_at=timezone.now() + timedelta(hours=1),
            responsible=self.user,
            created_by=self.user,
        )
        LeadTask.objects.create(
            lead=self.lead,
            kind=LeadTask.Kind.EMAIL,
            due_at=timezone.now() + timedelta(hours=2),
            responsible=self.user,
            created_by=self.user,
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("admin:leads_lead_changelist"))

        self.assertEqual(response.context["lead_counts"]["in_progress"], 1)

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

    def test_removal_dialog_requires_reason_and_confirmation(self):
        self.client.force_login(self.user)
        url = reverse("admin:leads_lead_delete", args=[self.lead.pk])

        response = self.client.get(url)
        missing_reason = self.client.post(
            url, {"post": "yes", "confirm_removal": "yes"}
        )
        missing_confirmation = self.client.post(
            url, {"post": "yes", "removal_reason": "Contato duplicado."}
        )

        self.assertContains(response, "Motivo de remover")
        self.assertContains(response, 'aria-label="Fechar"')
        self.assertContains(response, 'name="confirm_removal"')
        self.assertEqual(missing_reason.status_code, 200)
        self.assertEqual(missing_confirmation.status_code, 200)
        self.assertTrue(Lead.objects.filter(pk=self.lead.pk).exists())

    def test_confirmed_removal_deletes_and_logs_reason(self):
        self.client.force_login(self.user)
        lead_pk = self.lead.pk

        response = self.client.post(
            reverse("admin:leads_lead_delete", args=[lead_pk]),
            {
                "post": "yes",
                "removal_reason": "Solicitação duplicada recebida pelo site.",
                "confirm_removal": "yes",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Lead.objects.filter(pk=lead_pk).exists())
        log = LogEntry.objects.filter(
            object_id=str(lead_pk), action_flag=DELETION
        ).latest("action_time")
        self.assertIn("Solicitação duplicada", log.change_message)
