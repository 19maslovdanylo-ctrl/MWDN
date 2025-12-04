#!/bin/bash
set -e

echo "Starting read replica initialization..."

echo "Waiting for primary database to be ready..."
until PGPASSWORD=${POSTGRES_PASSWORD} pg_isready -h ${POSTGRES_PRIMARY_HOST} -p ${POSTGRES_PRIMARY_PORT} -U ${POSTGRES_USER}
do
  echo "Primary not ready yet, waiting..."
  sleep 2
done

echo "Primary database is ready!"

if [ ! -s "$PGDATA/PG_VERSION" ]; then
    echo "Empty data directory detected. Setting up read replica..."

    rm -rf ${PGDATA}/*

    echo "Creating base backup from primary..."
    PGPASSWORD=${POSTGRES_REPLICATION_PASSWORD} pg_basebackup \
        -h ${POSTGRES_PRIMARY_HOST} \
        -p ${POSTGRES_PRIMARY_PORT} \
        -U ${POSTGRES_REPLICATION_USER} \
        -D ${PGDATA} \
        -Fp -Xs -P -R

    echo "Base backup completed!"

    echo "hot_standby = on" >> ${PGDATA}/postgresql.conf

    echo "Read replica setup complete!"
else
    echo "Data directory already initialized, skipping base backup"
fi

# Start PostgreSQL
echo "Starting PostgreSQL in recovery mode..."
exec docker-entrypoint.sh postgres
