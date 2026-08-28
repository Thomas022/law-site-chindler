from getpass import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from properties.roles import ADMINISTRATOR_GROUP, EDITOR_GROUP


class Command(BaseCommand):
    help = "Cria um usuário da equipe e o associa ao perfil Administrador ou Editor."

    def add_arguments(self, parser):
        parser.add_argument("username", help="Nome de usuário para o painel")
        parser.add_argument("email", help="E-mail único para login e recuperação")
        parser.add_argument(
            "--role",
            required=True,
            choices=(ADMINISTRATOR_GROUP, EDITOR_GROUP),
            help="Perfil de acesso do usuário",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        user_model = get_user_model()
        username = options["username"].strip()
        email = options["email"].strip().lower()
        role = options["role"]

        if user_model.objects.filter(username__iexact=username).exists():
            raise CommandError("Já existe um usuário com esse nome.")
        if user_model.objects.filter(email__iexact=email).exists():
            raise CommandError("Já existe um usuário com esse e-mail.")

        password = getpass("Senha: ")
        confirmation = getpass("Confirme a senha: ")
        if password != confirmation:
            raise CommandError("As senhas informadas são diferentes.")

        candidate = user_model(username=username, email=email)
        try:
            validate_password(password, user=candidate)
        except ValidationError as exc:
            raise CommandError(" ".join(exc.messages)) from exc

        candidate.set_password(password)
        candidate.is_staff = True
        candidate.save()
        candidate.groups.add(Group.objects.get(name=role))

        self.stdout.write(
            self.style.SUCCESS(
                f"Usuário {username} criado com o perfil {role}."
            )
        )
