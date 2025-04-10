FROM python:3.10-slim-bullseye

WORKDIR /usr/src/app
ENV PYTHONPATH=/usr/src/app
ENV GIT_TERMINAL_PROMPT=0
ENV RUN_ENV=production
# Cloud Run default port
ENV PORT=8080   

ARG REVISION_ID
ENV REVISION_ID=$REVISION_ID

ARG DEPLOY_DATE
ENV DEPLOY_DATE=$DEPLOY_DATE

RUN apt-get update && apt-get  install git -y

COPY requirements.txt ./requirements.txt

RUN --mount=type=cache,target=/var/cache/pip \
    pip install \
    --only-binary ":all:" \
    --cache-dir /var/cache/pip \
    -r requirements.txt

COPY score/ /usr/src/app/score/
RUN python -m compileall score
RUN env CACHE_LOCATION=/tmp python -m score.app

CMD ["sh", "-c", "fastapi run score/app.py --port ${PORT}"]
