#!/bin/bash

# Config CGI script
echo "Content-Type: application/json"
echo ""

# Return current config
if [ -f ../data/config.yaml ]; then
    cat ../data/config.yaml
else
    echo '{}'
fi
