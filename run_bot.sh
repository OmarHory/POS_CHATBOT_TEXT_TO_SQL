
#!/bin/bash

env_file=".env"

if [ ! -f "$env_file" ]; then
    echo "Error: .env file not found in the current directory."
    exit 1
fi

gunicorn --bind 127.0.0.1:4000 src.app:app --chdir src --workers 4 --timeout 120
