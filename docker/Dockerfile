FROM python:3.9-slim as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

WORKDIR /wizznet

FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.1.6

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl wget build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./

# Install venv in workdir via poetry 
RUN poetry config virtualenvs.in-project true && poetry update && poetry install



FROM base as final 

COPY --from=builder /wizznet /wizznet

# copy shared certs and settings file into /data folder
#COPY docker/data /home/jimi/data

COPY plugins /wizznet/plugins
COPY playbooks /wizznet/playbooks
COPY roles /wizznet/roles
COPY group_vars /wizznet/group_vars
COPY host_vars /wizznet/host_vars

WORKDIR /wizznet
# copy individual files over
COPY docker/entrypoint.sh ./
COPY ansible.cfg ./
COPY Makefile ./
COPY day0.yml post_operations_vm.yml single_operations.yml ./
COPY inventory.ini ./


RUN chmod 700 entrypoint.sh
ENV PATH="/wizznet/.venv/bin:$PATH"


CMD ["./entrypoint.sh"]


