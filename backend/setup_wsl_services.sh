#!/bin/bash
set -e

service postgresql start
service redis-server start

# Configure postgres
su - postgres -c "psql -c \"ALTER USER postgres WITH PASSWORD 'postgres';\""
su - postgres -c "psql -c \"CREATE DATABASE answer_evaluation;\"" || true
su - postgres -c "psql -c \"CREATE DATABASE ai_eval_db;\"" || true
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE answer_evaluation TO postgres;\""
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE ai_eval_db TO postgres;\""

PG_CONF=$(find /etc/postgresql -name postgresql.conf | head -n 1)
PG_HBA=$(find /etc/postgresql -name pg_hba.conf | head -n 1)

if [ -f "$PG_CONF" ]; then
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF"
fi

if [ -f "$PG_HBA" ]; then
    echo "host all all 0.0.0.0/0 md5" >> "$PG_HBA"
    echo "host all all ::0/0 md5" >> "$PG_HBA"
    echo "host all all all trust" >> "$PG_HBA"
fi

service postgresql restart
service redis-server restart

echo "SERVICES_CONFIGURED_SUCCESSFULLY"
