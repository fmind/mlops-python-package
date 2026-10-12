# syntax=docker/dockerfile:1
# Multi-stage, non-root image built with uv (https://docs.astral.sh/uv/guides/integration/docker/).

FROM python:3.14-slim@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170 AS build
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
# Build the venv on the base image's interpreter: `.python-version` would otherwise make
# uv download its exact patch into /root, which the final stage never copies.
ENV UV_PYTHON=/usr/local/bin/python3
ENV UV_PYTHON_DOWNLOADS=never
WORKDIR /app
# Pinned, not `:latest` — a floating tag is invisible to Dependabot's docker ecosystem.
COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /uvx /bin/
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --frozen --no-install-project --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev --no-editable

FROM python:3.14-slim@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170
ENV PYTHONUNBUFFERED=1
WORKDIR /app
# The runtime already contains its dependencies; remove unused pip and its bundled
# bootstrap wheel so their vendored packages do not add a second dependency stack.
RUN PIP_ROOT_USER_ACTION=ignore python -m pip uninstall --yes pip \
  && python -c "import ensurepip, pathlib, shutil; shutil.rmtree(pathlib.Path(ensurepip.__file__).parent)"
# Fixed numeric uid/gid: stable file ownership across rebuilds and bind mounts, and
# resolvable by a host that does not share this image's /etc/passwd.
RUN groupadd -g 10001 app && useradd -u 10001 -g app -m app
USER 10001:10001
COPY --from=build --chown=10001:10001 /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
# Smoke test: fail the build, not the deployment, when the entrypoint cannot start.
RUN ["bikes", "--help"]
ENTRYPOINT ["bikes"]
CMD ["--help"]
