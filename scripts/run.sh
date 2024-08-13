#!/bin/bash -xeo pipefail




export DATE="$(date +%Y-%m-%d)"

export ENVVARS="OUTPUT_ROOT=gcs://openteams-score-data/${DATE}"
echo "using DATE=$DATE"


# gcloud --project=openteams-score \
#     run jobs execute --region=us-west1 \
#     scrape-conda \
#     --update-env-vars "${ENVVARS}"  \
#     --wait

# gcloud --project=openteams-score \
#     run jobs execute --region=us-west1 \
#     scrape-pypi \
#     --update-env-vars "${ENVVARS}"  \
#     --wait

# gcloud --project=openteams-score \
#     run jobs execute --region=us-west1 \
#     agg-source-urls \
#     --update-env-vars "${ENVVARS}"  \
#     --wait

gcloud --project=openteams-score \
    run jobs execute --region=us-west1 \
    scrape-git \
    --update-env-vars "${ENVVARS}"  \
    --wait
