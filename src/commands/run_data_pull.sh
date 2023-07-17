#!/bin/bash

#activate virtualenv
cd /home/ubuntu/
. .venv/bin/activate
cd /home/ubuntu/bot/foodics_gpt/

# Check if the client ID parameter is provided
if [ -z "$1" ]; then
    echo "Client ID parameter is missing. Aborting."
    exit 1
fi

# Set the client ID
CLIENT_ID="$1"

# Set the log directory path
LOG_DIR="logs/$CLIENT_ID"

echo "Log directory: $LOG_DIR"

# Create the log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Get the current date and time
DATE_TIME=$(date +"%Y-%m-%d_%H-%M-%S")

# Log file path
LOG_FILE="$LOG_DIR/$DATE_TIME.log"

mkdir -p data/$CLIENT_ID/raw/updates
mkdir -p data/$CLIENT_ID/processed/updates

python data_pipeline/pull_orders.py --client-id "$CLIENT_ID" --upload_s3 True

# Command 1: Run the first script
python data_pipeline/prepare_data.py --client-id "$CLIENT_ID" --mode pull >> "$LOG_FILE" 2>&1

# Check the exit status of the first command
EXIT_STATUS=$?
if [ $EXIT_STATUS -ne 0 ]; then
    # The first command failed, so don't proceed to the second command
    echo "Pulling data from source Failed with exit status $EXIT_STATUS. Aborting." >> "$LOG_FILE"
    exit 1
fi

# Command 2: Run the second script
python src/pos_driver.py --client-id "$CLIENT_ID" >> "$LOG_FILE" 2>&1

# Check the exit status of the second command
EXIT_STATUS=$?
if [ $EXIT_STATUS -ne 0 ]; then
    echo "Inserting updated data has Failed with exit status $EXIT_STATUS." >> "$LOG_FILE"
fi
