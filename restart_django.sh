#!/bin/bash

# Find the process ID (PID) running on port 8005
PID=$(pgrep -f "gunicorn.*:8005")

# If a process is found, kill it
if [ -n "$PID" ]; then
    echo "Killing process $PID running on port 8005"
    kill -9 $PID
fi

# BASE_DIR에 logs 폴더가 없다면 생성
if [ ! -d "logs" ]; then
    mkdir logs
fi

# Restart the Django server
echo "Starting Django(Gunicorn) server..."
gunicorn --bind 0.0.0.0:8005 server.wsgi:application > /tmp/gunicorn.log 2>&1 &