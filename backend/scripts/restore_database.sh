#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ] || [ -z "${DATABASE_URL:-}" ]; then
  echo "Uso: DATABASE_URL=... ./scripts/restore_database.sh caminho-do-backup.dump" >&2
  exit 1
fi

pg_restore --clean --if-exists --no-owner --no-acl --dbname="$DATABASE_URL" "$1"
echo "Restauração concluída a partir de: $1"
