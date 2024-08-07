#!/usr/bin/env bash

# The number of tasks defined in the --tasks parameter.
export TOTAL_PARTITIONS="${CLOUD_RUN_TASK_COUNT}"

# The index of this task. Starts at 0 for the first task and increments by 1 
# for every successive task, up to the maximum number of tasks minus 1. 
# If you set --parallelism to greater than 1, tasks might not follow the index order. 
# For example, it would be possible for task 2 to start before task 1.
export CURRENT_PARTITION="${CLOUD_RUN_TASK_INDEX}"


echo "--- ENVIRONMENT ---"
echo "OUTPUT_ROOT=${OUTPUT_ROOT}"
echo "TOTAL_PARTITIONS=${TOTAL_PARTITIONS}"
echo "CURRENT_PARTITION=${CURRENT_PARTITION}"
echo "ARGUMENTS" $@

# TODO: 
# Call python -m "score.cli" $@