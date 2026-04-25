FROM astral/uv:trixie-slim AS base

RUN apt-get update && \
    apt-get install --yes ca-certificates && \
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

COPY main.py .
COPY --parents=true memebot .

# Run test build.
FROM base AS test

RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-cache --all-groups

COPY . .
