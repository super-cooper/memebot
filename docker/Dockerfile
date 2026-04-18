FROM astral/uv:trixie-slim AS base
WORKDIR /opt/memebot/
CMD ["uv", "run", "main.py"]

# Run release build.
FROM base AS release
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-dev
COPY memebot main.py ./

# Run test build.
FROM base AS test
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --all-groups
COPY . .
