#!/bin/bash

# Status CGI script
echo "Content-Type: application/json"
echo ""

# Get miproxy status
if pgrep -f "miproxy" > /dev/null; then
    echo '{"status": "running"}'
else
    echo '{"status": "stopped"}'
fi
