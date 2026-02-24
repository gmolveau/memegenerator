# Developer Guide

## The app

A fullstack meme generator. Users browse a library of image templates, compose text and image overlays on top, apply image effects, and download the result as a JPG. Template metadata is managed through an admin panel.

---

## Repository layout

```console
meme-generator/
├── backend/          # Python / FastAPI API
├── frontend/         # SvelteKit SPA
├── docs/             # This documentation
│   ├── dev.md        # ← you are here
│   ├── env.md        # All environment variables and defaults
│   └── admin.md      # Admin panel usage guide
├── .env.dev.example  # Example backend env file for development
├── .env.prod.example # Example backend env file for production
└── Makefile          # Top-level convenience targets
```

---

## Getting started

### Prerequisites

| Tool          | Purpose                | Install                                            |
| ------------- | ---------------------- | -------------------------------------------------- |
| Python ≥ 3.13 | Backend runtime        | [python.org](https://python.org)                   |
| `uv`          | Python package manager | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js ≥ 20  | Frontend runtime       | [nodejs.org](https://nodejs.org)                   |
| `pnpm`        | Node package manager   | `npm i -g pnpm`                                    |

### First-time setup

```bash
# Install all dependencies (backend + frontend)
make install-dev

# Copy and configure environment files
cp .env.dev.example .env          # backend — edit as needed
cp frontend/.env.example frontend/.env  # frontend — if it exists
```

See [`docs/env.md`](env.md) for every available variable and its default value.

### Running locally

Open two terminals.

**Backend** (port 8000)

```bash
cd backend
make migrate       # apply any pending DB migrations (first run + after pulling changes)
make run-dev       # uvicorn with --reload
```

**Frontend** (port 5173)

```bash
cd frontend
make run-dev       # Vite dev server
```

The app is then available at <http://localhost:5173>.
Interactive API docs: <http://localhost:8000/docs>.

---

## Architecture overview

```console
Browser
  │  HTTP (REST JSON + multipart)
  ▼
FastAPI  ──────  SQLite (SQLAlchemy / Alembic)
  │
  └──  Storage disk  ──  Local FS  (default)
                    └──  AWS S3 / S3-compatible  (optional)
```

The frontend is a **pure client-side SPA** — it never does server-side rendering. All data comes from the backend API. Meme composition and JPG export happen entirely in the browser.

---

## Backend

### Stack

| Library            | Role                                             |
| ------------------ | ------------------------------------------------ |
| FastAPI            | HTTP framework, request validation, OpenAPI docs |
| SQLAlchemy 2 (ORM) | Database access                                  |
| Alembic            | Schema migrations                                |
| Pydantic           | Request / response schemas                       |
| boto3              | S3 storage driver                                |
| uv                 | Package and virtual-env management               |
| ruff               | Linter + formatter                               |
| ty                 | Static type checker                              |
| bandit             | Security linter                                  |

### Source layout

```console
backend/src/
├── main.py              # App factory: CORS, middleware, router registration
├── db/
│   ├── database.py      # Engine, session factory, get_db() dependency
│   └── migrations/      # Alembic env + versioned migration scripts
├── models/
│   └── template.py      # SQLAlchemy ORM model
├── schemas/
│   └── template.py      # Pydantic request / response schemas
├── services/
│   └── templates.py     # Business logic (DB queries, file handling)
├── routes/
│   └── templates.py     # FastAPI router — thin HTTP layer only
└── storage/
    ├── disk.py          # StorageDisk abstract base class
    ├── local.py         # LocalDisk implementation (dev default)
    └── s3.py            # S3Disk implementation
```

### Request lifecycle

```console
Route handler (src/routes/)
  → calls service function (src/services/)
     → queries DB via SQLAlchemy session
     → reads / writes files via StorageDisk
  → builds Pydantic response schema
  → returns JSON
```

Route handlers are intentionally thin — no business logic. Keep domain rules in `services/`.

### Storage abstraction

`StorageDisk` (defined in `storage/disk.py`) exposes four methods: `save`, `delete`, `url`, `ensure`. The active implementation is selected at startup from `STORAGE_DRIVER` and exposed as a FastAPI dependency via `get_disk()`. Add a new driver by subclassing `StorageDisk` and registering it in `storage/__init__.py`.

### Database migrations

```bash
# After editing a model, generate a migration
make new-migrate NAME=describe_your_change

# Apply all pending migrations
make migrate

# Check that models and DB are in sync (runs in CI)
make alembic-check
```

Migration files live in `src/db/migrations/versions/`. Name them clearly — the auto-generated message becomes the filename.

### Checks and formatting

```bash
make format    # ruff fix + format (run before committing .py files)
make checks    # ty + ruff-check + bandit (same as CI)
```

---

## Frontend

### Stack

| Tool                   | Role                    |
| ---------------------- | ----------------------- |
| SvelteKit 2 + Svelte 5 | Framework and routing   |
| TypeScript (strict)    | Type safety             |
| Tailwind CSS 4         | Utility-first styling   |
| Vite                   | Build tool / dev server |
| pnpm                   | Package manager         |

Full frontend architecture detail: [`frontend/README.md`](../frontend/README.md).

### Source layout

```console
frontend/src/
├── lib/
│   ├── api/
│   │   └── templates.ts       # HTTP client — all backend calls go here
│   ├── types/
│   │   └── index.ts           # Shared TypeScript interfaces
│   ├── stores/
│   │   └── editor.svelte.ts   # Global editor state (Svelte 5 runes singleton)
│   └── components/
│       ├── MemeEditor.svelte       # Canvas + toolbar + layer panel
│       ├── TextLayerEl.svelte      # Draggable / resizable / rotatable text layer
│       ├── ImageLayerEl.svelte     # Draggable / resizable / rotatable image layer
│       ├── TemplateGallery.svelte  # Search + grid of templates
│       └── TemplateUploadForm.svelte  # Upload form (name, keywords, file)
└── routes/
    ├── +layout.svelte     # Root layout — imports Tailwind
    ├── +page.svelte       # / — template gallery (home)
    ├── editor/
    │   └── +page.svelte   # /editor — meme editor (redirects to / if no template)
    └── admin/
        └── +page.svelte   # /admin — template metadata management
```

### State flow

```console
/ (+page.svelte)
  user selects template
    → editor.setTemplate(template)   ← store in editor.svelte.ts
    → goto('/editor')

/editor (+page.svelte)
  reads editor.template, editor.textLayers, editor.imageLayers …
  mutations go through editor.addTextLayer(), editor.updateTextLayer() …
```

The editor store is a module-level singleton that survives client-side navigation. On a hard refresh of `/editor`, `editor.template` is `null` and the page redirects to `/`.

### Adding a new API call

1. Add the function to `src/lib/api/templates.ts`.
2. Import and call it from the relevant component or store.
3. Keep all `fetch` calls inside `src/lib/api/` — never inline them in components.

### Checks and formatting

```bash
make format    # Prettier (run before committing .ts / .svelte / .html files)
make checks    # ESLint
```

---

## Make targets (quick reference)

Run `make help` in any directory to see available targets.

| Directory   | Target                    | What it does                                |
| ----------- | ------------------------- | ------------------------------------------- |
| root        | `make install-dev`        | Install backend + frontend dependencies     |
| root        | `make format`             | Format all code                             |
| `backend/`  | `make run-dev`            | Start API server with hot reload            |
| `backend/`  | `make migrate`            | Apply pending DB migrations                 |
| `backend/`  | `make new-migrate NAME=x` | Generate a new migration from model changes |
| `backend/`  | `make checks`             | ty + ruff + bandit                          |
| `frontend/` | `make run-dev`            | Start Vite dev server                       |
| `frontend/` | `make checks`             | ESLint                                      |

---

## Documentation index

| File                                          | Contents                                                  |
| --------------------------------------------- | --------------------------------------------------------- |
| [`docs/dev.md`](dev.md)                       | This file — architecture and getting started              |
| [`docs/env.md`](env.md)                       | All environment variables, defaults, and example configs  |
| [`docs/admin.md`](admin.md)                   | Admin panel user guide                                    |
| [`frontend/README.md`](../frontend/README.md) | Deep dive into frontend architecture, canvas export, CORS |
| `http://localhost:8000/docs`                  | Auto-generated OpenAPI / Swagger UI (backend running)     |
| `http://localhost:8000/redoc`                 | ReDoc alternative API docs                                |
