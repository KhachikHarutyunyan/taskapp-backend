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
import socket, time, os
host = os.environ.get('REDIS_HOST', 'localhost')
port = int(os.environ.get('REDIS_PORT', 6379))
password = os.environ.get('REDIS_PASSWORD', '')

while True:
    try:
        s = socket.create_connection((host, port), timeout=2)
        if password:
            s.sendall(f'AUTH {password}\r\n'.encode())
            resp = s.recv(1024)
            if b'+OK' not in resp:
                print('Redis auth failed. Check REDIS_PASSWORD.')
                time.sleep(2)
                continue
        
        s.sendall(b'PING\r\n')
        resp = s.recv(1024)
        if b'PONG' in resp:
            s.close()
            break
    except Exception as e:
        print(f'Redis connection error: {e}')
    time.sleep(2)
" && echo "Redis is up!"
}

wait_for_postgres
wait_for_redis

echo "Running database migrations..."
alembic upgrade head

echo "Starting FastAPI application..."
exec "$@"