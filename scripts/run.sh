#!/bin/bash -xeo pipefail




export DATE="$(date +%Y-%m-%d).1"

export ENVVARS="OUTPUT_ROOT=gcs://openteams-score-data/${DATE}"
echo "using DATE=$DATE"

date
gcloud --project=openteams-score \
    run jobs execute --region=us-west1 \
    scrape-conda \
    --update-env-vars "${ENVVARS}"  \
    --wait

date
gcloud --project=openteams-score \
    run jobs execute --region=us-west1 \
    scrape-pypi \
    --update-env-vars "${ENVVARS}"  \
    --wait

date
gcloud --project=openteams-score \
    run jobs execute --region=us-west1 \
    agg-source-urls \
    --update-env-vars "${ENVVARS}"  \
    --wait

date
gcloud --project=openteams-score \
    run jobs execute --region=us-west1 \
    scrape-git \
    --update-env-vars "${ENVVARS}"  \
    --wait
