#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chindler_backend.settings.local")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django não está instalado. Instale as dependências de backend antes de continuar."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
