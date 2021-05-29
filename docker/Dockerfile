FROM python:3.9-slim as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

WORKDIR /home/jimi

FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.1.6

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl wget openssl build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install "poetry==$POETRY_VERSION"

COPY docker/jimi-core/pyproject.toml docker/jimi-core/poetry.lock ./

# Install venv in workdir via poetry 
RUN poetry config virtualenvs.in-project true && poetry update && poetry install

# directory works
RUN mkdir data && mkdir data/log && mkdir plugins
WORKDIR /home/jimi/data

#RUN wget https://raw.githubusercontent.com/z1pti3/jimi-docker/master/data/settings.json
#COPY docker/shared/settings.json ./



FROM base as final

# Requires git for Batfish 
RUN apt-get update && \
    apt-get install -y --no-install-recommends git  && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /home/jimi /home/jimi

# copy shared certs and settings file into /data folder
#COPY docker/data /home/jimi/data

COPY core /home/jimi/core
COPY system /home/jimi/system
COPY screens /home/jimi/screens
# is needed for core? make sure to check this
COPY web /home/jimi/web
COPY react-web /home/jimi/react-web

WORKDIR /home/jimi

COPY jimi_core.py jimi_cli.py jimi.py docker/jimi-core/entrypoint.sh ./

# copy shared certs and settings file into /data folder
COPY docker/settings/settings.json data/settings.json

RUN chmod 700 entrypoint.sh
ENV PATH="/jimi/.venv/bin:$PATH"

# test env vars for jimi db
#ENV DB=jimi-db

CMD ["./entrypoint.sh"]


