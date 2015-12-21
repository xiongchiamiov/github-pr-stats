FROM python:2

RUN apt-get update && apt-get install -q -y git

RUN pip install --upgrade setuptools && pip install --upgrade pip && pip install github-pr-stats

ENTRYPOINT [ "github-pr-stats" ]

