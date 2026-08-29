from django.db import transaction
from django.utils import timezone

from .models import Lead


@transaction.atomic
def anonymize_lead(lead):
    if lead.anonymized_at is not None:
        return False
    lead.name = "Dados anonimizados"
    lead.phone = ""
    lead.email = f"anonimizado-{lead.pk}@invalid.local"
    lead.message = "Conteúdo removido após o prazo de retenção."
    lead.responsible = None
    lead.status = Lead.Status.DISCARDED
    lead.anonymized_at = timezone.now()
    lead.save(
        update_fields=(
            "name",
            "phone",
            "email",
            "message",
            "responsible",
            "status",
            "anonymized_at",
            "updated_at",
        )
    )
    lead.interactions.update(
        description="Conteúdo removido após o prazo de retenção.",
        outcome="",
        created_by=None,
    )
    lead.tasks.update(notes="", responsible=None, created_by=None)
    return True
