FROM python:3.10-slim-bullseye

WORKDIR /usr/src/app
ENV PYTHONPATH=/usr/src/app
ENV GIT_TERMINAL_PROMPT=0

ARG REVISION_ID
ENV REVISION_ID=$REVISION_ID

RUN apt-get update && apt-get  install git -y

COPY requirements.txt ./requirements.txt

RUN --mount=type=cache,target=/var/cache/pip \
    pip install \
    --only-binary ":all:" \
    --cache-dir /var/cache/pip \
    -r requirements.txt

RUN python -m compileall /usr/local/lib/python3.10/site-packages

COPY score/ /usr/src/app/score/
RUN python -m compileall score

COPY run_script.sh /usr/src/app/run_script.sh

CMD /usr/src/app/run_script.sh

