#!/bin/bash

# Get the current date in YYYY.MM.DD format
current_date=$(date +"%Y-%m-%d")

# Create the JSON object with the current date
DATA=$(cat <<EOF
{
  "output_root": "gs://openteams-score-data/$current_date"
}
EOF
)

# Export the DATA variable so it's available to child processes
export DATA

# Print the DATA variable (optional, for verification)
echo "DATA has been set to:"
echo "$DATA"

# Run the gcloud command with the DATA variable
gcloud workflows run score-workflow --data="$DATA"
