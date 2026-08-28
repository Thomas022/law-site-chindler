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

    property = models.ForeignKey(
        Property,
        verbose_name="imóvel",
        related_name="leads",
        null=True,
        on_delete=models.SET_NULL,
    )
    property_title = models.CharField("título do imóvel", max_length=180)
    name = models.CharField("nome", max_length=150)
    phone = models.CharField("telefone", max_length=30)
    email = models.EmailField("e-mail")
    message = models.TextField("mensagem")
    status = models.CharField(
        "situação", max_length=20, choices=Status.choices, default=Status.NEW
    )
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="responsável",
        related_name="assigned_leads",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    consent_version = models.CharField("versão do consentimento", max_length=30)
    consent_at = models.DateTimeField("consentimento registrado em")
    last_interaction_at = models.DateTimeField(
        "último atendimento em", null=True, blank=True
    )
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
        ]

    def __str__(self):
        return f"{self.name} — {self.property_title}"

    @builtins.property
    def retention_deadline(self):
        reference_date = self.last_interaction_at or self.created_at
        if reference_date is None:
            reference_date = timezone.now()
        return reference_date + timedelta(days=730)
