set shell := ["bash", "-euo", "pipefail", "-c"]
set dotenv-load := true

default:
    @just --list

### docker compose dev stack

dev-up:
    [ -f .env ] || cp .env.dev.example .env
    docker compose build --pull
    docker compose watch

dev-stop:
    docker compose down

dev-clean:
    docker compose down --volumes

dev-backend-shell:
    docker compose exec backend bash

### local dev stack

run-keycloak:
    docker run --rm -p 8080:8080 -e KEYCLOAK_ADMIN=keycloak -e KEYCLOAK_ADMIN_PASSWORD=keycloak -v ./keycloak/realm-export.json:/opt/keycloak/data/import/realm-export.json quay.io/keycloak/keycloak:24.0.0 start-dev --import-realm

### docker compose fake prod stack

localprod-up:
    [ -f .env ] || (echo "missing .env"; exit 1)
    docker compose -f compose.localprod.yml build --pull
    docker compose -f compose.localprod.yml up -d

localprod-stop:
    docker compose -f compose.localprod.yml down

localprod-clean:
    docker compose -f compose.localprod.yml down --volumes

### misc

install-dev:
    cd backend && just install-dev
    cd frontend && just install-dev

format:
    cd backend && just format
    cd frontend && just format

clean:
    cd backend && just clean
    cd frontend && just clean
