#!/usr/bin/env sh
set -eu

if [ -z "${DATABASE_URL:-}" ]; then
  echo "Defina DATABASE_URL antes de executar o backup." >&2
  exit 1
fi

backup_directory="${BACKUP_DIRECTORY:-./backups}"
mkdir -p "$backup_directory"
backup_file="$backup_directory/chindler_$(date +%Y%m%d_%H%M%S).dump"

pg_dump --format=custom --no-owner --no-acl --file="$backup_file" "$DATABASE_URL"
echo "Backup criado em: $backup_file"
