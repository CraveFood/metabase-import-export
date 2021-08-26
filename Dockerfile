FROM python:3.8-slim-buster

ENV VERSION=0.2.3

WORKDIR /app

COPY . .

RUN python3 setup.py sdist && pip install dist/metabase-import-export-${VERSION}.tar.gz

ENTRYPOINT ["metabase-import-export"]
