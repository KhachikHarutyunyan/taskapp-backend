#!/bin/bash
set -e

wait_for_postgres() {
    echo "Waiting for PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."
    python3 -c "
import socket, time
while True:
    try:
        s = socket.create_connection(('$POSTGRES_HOST', $POSTGRES_PORT), timeout=2)
        s.close()
        break
    except Exception:
        time.sleep(2)
" && echo "PostgreSQL is up!"
}

wait_for_redis() {
    echo "Waiting for Redis at $REDIS_HOST:$REDIS_PORT..."
    python3 -c "
import socket, time
while True:
    try:
        s = socket.create_connection(('$REDIS_HOST', $REDIS_PORT), timeout=2)
        # Аутентификация, если пароль задан
        if '$REDIS_PASSWORD':
            s.sendall(b'AUTH $REDIS_PASSWORD\r\n')
            resp = s.recv(1024)
            if b'+OK' not in resp:
                raise Exception('Redis authentication failed')
        # Проверка доступности
        s.sendall(b'PING\r\n')
        resp = s.recv(1024)
        if b'PONG' in resp:
            s.close()
            break
    except Exception:
        pass
    time.sleep(2)
" && echo "Redis is up!"
}

wait_for_postgres
wait_for_redis

echo "Running database migrations..."
alembic upgrade head

echo "Starting FastAPI application..."
exec "$@"