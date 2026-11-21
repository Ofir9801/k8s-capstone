#!/bin/bash
# Run by the wait-for-db init container (see wait-for-db-patch.yaml): blocks until
# MariaDB answers and the todos table exists, so the API starts against a ready database.
# Uses MYSQL_HOST, MYSQL_USER, MYSQL_DB, MYSQL_TABLE (todolist-config) and MYSQL_PASSWORD.
set -e
until mariadb -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1;" >/dev/null 2>&1; do
  echo "waiting for database at $MYSQL_HOST..."
  sleep 2
done
until mariadb -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" \
      -e "SELECT 1 FROM \`$MYSQL_DB\`.\`$MYSQL_TABLE\` LIMIT 1;" >/dev/null 2>&1; do
  echo "waiting for table $MYSQL_DB.$MYSQL_TABLE to be ready..."
  sleep 2
done
echo "database and table are ready"
