#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER ${POSTGRES_REPLICATION_USER} WITH REPLICATION ENCRYPTED PASSWORD '${POSTGRES_REPLICATION_PASSWORD}';
EOSQL

cat >> ${PGDATA}/postgresql.conf <<EOF
wal_level = replica
max_wal_senders = 3
max_replication_slots = 3
hot_standby = on
EOF

echo "host replication ${POSTGRES_REPLICATION_USER} 0.0.0.0/0 md5" >> ${PGDATA}/pg_hba.conf

echo "Primary database configured for replication"
