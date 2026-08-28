from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Verifica a conexão ativa com o banco de dados."

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        database_name = connection.settings_dict.get("NAME", "")
        self.stdout.write(
            self.style.SUCCESS(
                f"Banco conectado: fornecedor={connection.vendor}, nome={database_name}"
            )
        )
