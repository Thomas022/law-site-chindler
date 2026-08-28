from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models.functions import Coalesce
from django.utils import timezone

from leads.models import Lead
from leads.services import anonymize_lead


class Command(BaseCommand):
    help = "Anonimiza interessados cujo prazo de retenção de dois anos terminou."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Informa quantos registros seriam anonimizados sem alterá-los.",
        )

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=730)
        expired = (
            Lead.objects.filter(anonymized_at__isnull=True)
            .annotate(retention_reference=Coalesce("last_interaction_at", "created_at"))
            .filter(retention_reference__lt=cutoff)
        )
        count = expired.count()
        if options["dry_run"]:
            self.stdout.write(f"{count} interessado(s) seriam anonimizados.")
            return
        processed = sum(anonymize_lead(lead) for lead in expired.iterator())
        self.stdout.write(self.style.SUCCESS(f"{processed} interessado(s) anonimizados."))

