FROM python:2

RUN pip install --upgrade setuptools && pip install --upgrade pip && pip install github-pr-stats

ENTRYPOINT [ "github-pr-stats" ]

