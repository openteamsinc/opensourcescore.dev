#!/usr/bin/env bash

# The number of tasks defined in the --tasks parameter.
export SCORE_NUM_PARTITIONS="${CLOUD_RUN_TASK_COUNT}"

# The index of this task. Starts at 0 for the first task and increments by 1 
# for every successive task, up to the maximum number of tasks minus 1. 
# If you set --parallelism to greater than 1, tasks might not follow the index order. 
# For example, it would be possible for task 2 to start before task 1.
export SCORE_PARTITION="${CLOUD_RUN_TASK_INDEX}"


echo "--- ENVIRONMENT ---"
echo "COMMAND=${COMMAND}"
echo "OUTPUT_ROOT=${OUTPUT_ROOT}"
echo "SCORE_NUM_PARTITIONS=${SCORE_NUM_PARTITIONS}"
echo "SCORE_PARTITION=${SCORE_PARTITION}"

python -m score.cli "${COMMAND}"
