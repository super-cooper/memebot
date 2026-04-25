FROM astral/uv:trixie-slim AS base

# hadolint global ignore=DL3008  # We always want the latest ca-certificates
RUN apt-get update && \
    apt-get install --yes --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd --gid 1000 memebot && \
    useradd --gid 1000 --uid 1000 --create-home memebot

USER memebot

WORKDIR /opt/memebot/

CMD ["uv", "run", "main.py"]

FROM base AS release

RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-cache --no-dev

COPY main.py main.py
COPY memebot memebot

# Run test build.
FROM base AS test

RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-cache --all-groups

COPY . .
