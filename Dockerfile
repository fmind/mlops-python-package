# syntax=docker/dockerfile:1
# Multi-stage, non-root image built with uv (https://docs.astral.sh/uv/guides/integration/docker/).

FROM python:3.14-slim AS build
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --frozen --no-install-project --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev --no-editable

FROM python:3.14-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd -r app && useradd -r -g app -m app
USER app
COPY --from=build --chown=app:app /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["bikes"]
CMD ["--help"]
