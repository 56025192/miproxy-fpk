#!/bin/bash

# Auth CGI script
echo "Content-Type: application/json"
echo ""

# Simple auth check - in production, implement proper authentication
auth_header=$(http_auth 2>/dev/null || echo "")

if [ -n "$auth_header" ]; then
    echo '{"authenticated": true}'
else
    echo '{"authenticated": false}'
fi
