# Deployment Guide

## Prerequisites

- A container orchestration runtime (docker compose, kubernetes...)
- A running OIDC provider (Keycloak recommended — see below)

## Docker images

Images are published to GitHub Container Registry on every semver tag by the CI workflow:

```console
ghcr.io/<owner>/memegenerator/backend:<version>
ghcr.io/<owner>/memegenerator/frontend:<version>
```

Both images are built for `linux/amd64` and `linux/arm64`.

## Running in production

The repo ships `compose.localprod.yml` as a reference stack. It includes Traefik as a reverse proxy, the backend, the frontend, an oidc provider, and a one-shot migration service that runs Alembic before the backend starts.

Use this compose stack to easily try the app.

```bash
cp .env.prod.example .env
# fill in .env
just localprod-up
```

Verify the deployment:

```bash
curl https://app.example.com/api/health
# {"status":"ok","version":"<version>"}
```

The app is available at <http://app.localhost>

## Configuration

All configuration is done via environment variables. See [env.md](env.md) for the full reference.

## OIDC setup

Any OIDC-compliant provider works. The backend only needs the three endpoint URLs and a confidential client.

First, login using the future `superadmin` user.

Then promote it to `superadmin` using the `cli` command :

```bash
uv run manage.py users make-superadmin --email "admin@example.com"
```

## Storage and persistence

By default the backend stores the SQLite database and uploaded images on the local filesystem. Mount both paths as volumes so data survives container restarts (`DATA_FOLDER`, `STATIC_FOLDER` in `.env`).

For multiple backend replicas, switch to an external database (`DATABASE_URL`) and S3-compatible storage (`STORAGE_DRIVER=s3`). See [env.md](env.md) for the S3 variables.

## Observability

Set `OTEL_ENABLED=true` and `OTEL_EXPORTER_OTLP_ENDPOINT` to send traces to any OTLP-compatible collector (Jaeger, Grafana Tempo, Honeycomb...). Trace IDs are automatically injected into structured log lines for correlation. See [dev.md](dev.md) for details.
