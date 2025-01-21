#!/bin/bash

# Find the process ID (PID) running on port 8005
PID=$(lsof -t -i:8005)

# If a process is found, kill it
if [ -n "$PID" ]; then
    echo "Killing process $PID running on port 8005"
    kill -9 $PID
fi

# Restart the Django server
echo "Starting Django server..."
nohup python manage.py runserver 0.0.0.0:8005 > /tmp/nohup.log 2>&1 &