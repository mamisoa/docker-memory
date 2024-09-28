#!/bin/bash
set -e
echo "Creating user..."
echo "Current PATH: $PATH"
echo "Current working directory: $(pwd)"

mariadb -u root -p${MYSQL_ROOT_PASSWORD} <<-EOSQL
    CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';
    GRANT ALL PRIVILEGES ON ${MYSQL_DATABASE}.* TO '${MYSQL_USER}'@'%';
    FLUSH PRIVILEGES;
EOSQL
