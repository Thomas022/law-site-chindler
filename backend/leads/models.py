import builtins
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from properties.models import Property


class Lead(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Novo"
        IN_PROGRESS = "in_progress", "Em atendimento"
        VISIT_SCHEDULED = "visit_scheduled", "Visita agendada"
        COMPLETED = "completed", "Concluído"
        DISCARDED = "discarded", "Descartado"

    class Priority(models.TextChoices):
        NORMAL = "normal", "Normal"
        HIGH = "high", "Alta"
        URGENT = "urgent", "Urgente"

    class Source(models.TextChoices):
        WEBSITE = "website", "Site"
        PHONE = "phone", "Telefone"
        WHATSAPP = "whatsapp", "WhatsApp"
        REFERRAL = "referral", "Indicação"
        MANUAL = "manual", "Cadastro manual"

    property = models.ForeignKey(
        Property,
        verbose_name="imóvel",
        related_name="leads",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    property_title = models.CharField("título do imóvel", max_length=180, blank=True)
    name = models.CharField("nome", max_length=150)
    phone = models.CharField("telefone", max_length=30, blank=True)
    email = models.EmailField("e-mail")
    message = models.TextField("mensagem")
    status = models.CharField(
        "situação", max_length=20, choices=Status.choices, default=Status.NEW
    )
    priority = models.CharField(
        "prioridade", max_length=10, choices=Priority.choices, default=Priority.NORMAL
    )
    source = models.CharField(
        "origem", max_length=15, choices=Source.choices, default=Source.WEBSITE
    )
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="responsável",
        related_name="assigned_leads",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    consent_version = models.CharField("versão do consentimento", max_length=30, blank=True)
    consent_at = models.DateTimeField("consentimento registrado em", null=True, blank=True)
    last_interaction_at = models.DateTimeField(
        "último atendimento em", null=True, blank=True
    )
    discard_reason = models.TextField("motivo do descarte", blank=True)
    completed_at = models.DateTimeField("concluído em", null=True, blank=True)
    anonymized_at = models.DateTimeField("anonimizado em", null=True, blank=True)
    created_at = models.DateTimeField("recebido em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "interessado"
        verbose_name_plural = "interessados"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["responsible", "status"]),
            models.Index(fields=["last_interaction_at"]),
            models.Index(fields=["priority", "created_at"]),
        ]

    def __str__(self):
        return f"{self.name} — {self.property_title}"

    @builtins.property
    def retention_deadline(self):
        reference_date = self.last_interaction_at or self.created_at
        if reference_date is None:
            reference_date = timezone.now()
        return reference_date + timedelta(days=730)


class LeadInteraction(models.Model):
    class Kind(models.TextChoices):
        NOTE = "note", "Observação"
        CALL = "call", "Ligação"
        EMAIL = "email", "E-mail"
        WHATSAPP = "whatsapp", "WhatsApp"
        VISIT = "visit", "Visita"
        STATUS_CHANGE = "status_change", "Alteração de situação"
        ASSIGNMENT = "assignment", "Alteração de responsável"
        TASK_COMPLETED = "task_completed", "Tarefa concluída"

    lead = models.ForeignKey(
        Lead, verbose_name="interessado", related_name="interactions", on_delete=models.CASCADE
    )
    kind = models.CharField("tipo", max_length=20, choices=Kind.choices, default=Kind.NOTE)
    description = models.TextField("descrição")
    outcome = models.CharField("resultado", max_length=180, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="registrado por",
        related_name="lead_interactions",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    occurred_at = models.DateTimeField("ocorrido em", default=timezone.now)
    created_at = models.DateTimeField("registrado em", auto_now_add=True)

    class Meta:
        verbose_name = "interação"
        verbose_name_plural = "histórico de atendimento"
        ordering = ["-occurred_at", "-created_at"]
        indexes = [models.Index(fields=["lead", "-occurred_at"])]

    def __str__(self):
        return f"{self.get_kind_display()} — {self.lead}"


class LeadTask(models.Model):
    class Kind(models.TextChoices):
        CALL = "call", "Ligação"
        EMAIL = "email", "E-mail"
        WHATSAPP = "whatsapp", "WhatsApp"
        VISIT = "visit", "Visita"
        FOLLOW_UP = "follow_up", "Retorno"
        OTHER = "other", "Outro"

    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        COMPLETED = "completed", "Concluída"
        CANCELED = "canceled", "Cancelada"

    lead = models.ForeignKey(
        Lead, verbose_name="interessado", related_name="tasks", on_delete=models.CASCADE
    )
    kind = models.CharField("tipo", max_length=15, choices=Kind.choices)
    due_at = models.DateTimeField("data e horário")
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="responsável",
        related_name="lead_tasks",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    notes = models.CharField("observação", max_length=240, blank=True)
    status = models.CharField(
        "situação", max_length=10, choices=Status.choices, default=Status.PENDING
    )
    completed_at = models.DateTimeField("concluída em", null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="criada por",
        related_name="created_lead_tasks",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField("criada em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizada em", auto_now=True)

    class Meta:
        verbose_name = "próxima ação"
        verbose_name_plural = "próximas ações"
        ordering = ["due_at"]
        indexes = [
            models.Index(fields=["status", "due_at"]),
            models.Index(fields=["responsible", "status", "due_at"]),
        ]

    def __str__(self):
        return f"{self.get_kind_display()} em {self.due_at:%d/%m/%Y %H:%M}"

    @property
    def is_overdue(self):
        return self.status == self.Status.PENDING and self.due_at < timezone.now()
