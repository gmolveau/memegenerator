# meme-generator

[![Backend](https://img.shields.io/github/v/release/gmolveau/memegenerator?label=backend&logo=docker)](https://github.com/gmolveau/memegenerator/pkgs/container/memegenerator%2Fbackend)
[![Frontend](https://img.shields.io/github/v/release/gmolveau/memegenerator?label=frontend&logo=docker)](https://github.com/gmolveau/memegenerator/pkgs/container/memegenerator%2Ffrontend)
![Python](https://img.shields.io/badge/python-3.13+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.129+-009688?logo=fastapi&logoColor=white)
![Svelte](https://img.shields.io/badge/Svelte-5-FF3E00?logo=svelte&logoColor=white)

A fullstack webapp meme generator.

Browse a library of image templates, compose text and image overlays on a canvas, apply image effects, and download the result as a JPG.

## Stack

- **Backend**: FastAPI + SQLAlchemy + Alembic (Python) + SQLite
- **Frontend**: SvelteKit + Svelte 5 + Tailwind CSS
- **Auth**: OIDC (keycloak in dev mode)

## Developers

See [`docs/dev.md`](docs/dev.md) for full architecture and developer guide.
