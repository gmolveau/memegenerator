# Developer Guide

## The app

A fullstack meme generator. Users browse a library of image templates, compose text and image overlays on top, apply image effects, and download the result as a JPG. Template metadata is managed through an admin panel. Authentication is handled via Keycloak (OIDC).

---

## Repo layout

```console
meme-generator/
├── backend/          # Python / FastAPI API
├── frontend/         # SvelteKit SPA
├── keycloak/         # Keycloak realm export for local dev
├── docs/             # This documentation
│   ├── dev.md        # ← you are here
│   ├── env.md        # All environment variables and defaults
│   └── admin.md      # Admin panel usage guide
├── compose.yml            # Docker Compose dev stack
├── compose.localprod.yml  # Docker Compose local-prod stack
├── justfile               # Top-level convenience targets
├── .env.dev.example       # Example env file for development
└── .env.prod.example      # Example env file for production
```

---

## Getting started

### Prerequisites

| Tool          | Purpose                | Install                                                     |
| ------------- | ---------------------- | ----------------------------------------------------------- |
| Python ≥ 3.13 | Backend runtime        | [python.org](https://python.org)                            |
| `uv`          | Python package manager | `curl -LsSf https://astral.sh/uv/install.sh \| sh`          |
| Node.js ≥ 20  | Frontend runtime       | [nodejs.org](https://nodejs.org)                            |
| `pnpm`        | Node package manager   | `<https://pnpm.io/installation>                             |
| `just`        | Task runner            | `brew install just` / [docs](https://github.com/casey/just) |

### First-time setup

```bash
# Copy and configure environment files
cp .env.dev.example .env

# Install all dependencies (backend + frontend)
just install-dev
```

See [`docs/env.md`](env.md) for every available variable and its default value.

### Running locally

#### Without Docker Compose

Edit the Keycloak URL in `.env` and replace `http://keycloak.localhost` with `http://localhost:8080`.

Open 3 terminals.

**Backend** (port 8000)

```bash
cd backend
just migrate       # apply pending DB migrations (first run + after pulling changes)
just run-dev       # uvicorn with --reload
```

**Frontend** (port 5173)

```bash
cd frontend
just run-dev       # Vite dev server
```

**Keycloak** (port 8080)

```bash
just run-keycloak  # ephemeral Keycloak container
```

The app is available at <http://localhost:5173>.

Interactive API docs: <http://localhost:8000/api/docs>.

Keycloak admin: <http://localhost:8080> (user: `keycloak` / password: `keycloak`).

#### With Docker Compose

```bash
just dev-up
```

The app is available at <http://app.localhost>.

Interactive API docs: <http://app.localhost/api/docs>.

Keycloak: <http://keycloak.localhost>.

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
├── web.py               # App factory: CORS, middleware, router registration
├── config.py            # Settings loaded from environment via Pydantic
├── database.py          # Engine, session factory, get_db() dependency
├── dependencies.py      # Shared FastAPI dependencies (auth, current user)
├── models.py            # SQLAlchemy ORM models (User, Group, Role, Template)
├── migrations/          # Alembic env + versioned migration scripts
├── schemas/
│   └── template.py      # Pydantic request / response schemas
├── services/
│   ├── templates.py     # Business logic for templates (DB queries, file handling)
│   └── users.py         # Business logic for users (upsert on login)
├── routes/
│   ├── auth.py          # OAuth2 / Keycloak login, callback, logout, /auth/me
│   ├── health.py        # GET /health
│   └── templates.py     # FastAPI router — thin HTTP layer only
├── storage/
│   ├── disk.py          # StorageDisk abstract base class
│   ├── local.py         # LocalDisk implementation (dev default)
│   └── s3.py            # S3Disk implementation
└── cli/
    ├── main.py          # CLI entry point (typer app)
    ├── templates.py     # CLI commands for template management
    └── users.py         # CLI commands for user management
```

### Data model

| Model      | Key fields                                                                       |
| ---------- | -------------------------------------------------------------------------------- |
| `Template` | `name`, `filename`, `keywords`, `popularity`, `creator_id`, `text_layers` (JSON) |
| `User`     | `name`, `email`, `sub` (OIDC subject), `role_id`                                 |
| `Role`     | `name`                                                                           |
| `Group`    | `name`, `role_id`; many-to-many with `User`                                      |

`text_layers` is stored as a JSON string on the `Template` model and describes default text layers (position, size, font, color, alignment) that are pre-loaded when a user opens a template in the editor.

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

### Auth flow

Login uses the OAuth2 authorization code flow via Keycloak:

1. Frontend redirects to `GET /api/auth/login?next=<url>`
2. Backend redirects to Keycloak authorization endpoint
3. Keycloak redirects back to `GET /api/auth/callback`
4. Backend exchanges code for tokens, upserts the user in the DB, stores user ID in a signed session cookie
5. Backend redirects to `next`

The frontend calls `GET /api/auth/me` once on startup and caches the result in the `auth` store (see Frontend section). Subsequent page navigations do not re-request `/auth/me`.

### Storage abstraction

`StorageDisk` exposes four methods: `save`, `delete`, `url`, `ensure`. The active implementation is selected at startup from `STORAGE_DRIVER` and exposed as a FastAPI dependency via `get_disk()`. Add a new driver by subclassing `StorageDisk` and registering it in `storage/__init__.py`.

### Database migrations

```bash
# After editing a model, generate a migration
cd backend
just new-migrate name=describe_your_change

# Apply all pending migrations
just migrate

# Check that models and DB are in sync (runs in CI)
just alembic-check
```

Migration files live in `src/migrations/versions/`.

### Checks and formatting

```bash
cd backend
just format    # ruff fix + format
just checks    # ty + ruff-check + bandit
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

### Source layout

```console
frontend/src/
├── lib/
│   ├── api/
│   │   ├── auth.ts            # Auth API calls (login URL, logout, getMe)
│   │   ├── client.ts          # Base fetch wrapper
│   │   └── templates.ts       # Template CRUD and image upload
│   ├── types/
│   │   └── index.ts           # Shared TypeScript interfaces
│   ├── stores/
│   │   ├── auth.svelte.ts     # Auth store: tri-state undefined/null/User
│   │   └── editor.svelte.ts   # Global editor state (layers, template, effect)
│   └── components/
│       ├── AppHeader.svelte        # Shared header used by all pages
│       ├── MemeEditor.svelte       # Canvas + toolbar + layer list
│       ├── EditorToolbar.svelte    # Add layer, effects, download, save buttons
│       ├── LayerListPanel.svelte   # Sidebar list of layers with controls
│       ├── TextLayerEl.svelte      # Draggable / resizable / rotatable text layer
│       ├── ImageLayerEl.svelte     # Draggable / resizable / rotatable image layer
│       ├── layerInteractions.svelte.ts  # Shared drag/resize/rotate pointer logic
│       ├── TemplateGallery.svelte  # Paginated search grid of templates
│       ├── TemplateCard.svelte     # Single template card with inline edit
│       ├── TemplateEditorView.svelte   # Shared view for upload + template edit
│       ├── TemplateUploadForm.svelte   # Upload form (name, keywords, file)
│       └── PaginationBar.svelte    # Reusable pagination component
└── routes/
    ├── +layout.svelte          # Root layout — imports Tailwind, initialises auth
    ├── +page.svelte            # / — template gallery (home)
    ├── templates/
    │   ├── +page.svelte        # /templates — my templates
    │   ├── [id]/
    │   │   ├── +page.svelte    # /templates/<id> — meme editor
    │   │   └── edit/
    │   │       └── +page.svelte  # /templates/<id>/edit — template editor
    ├── upload/
    │   └── +page.svelte        # /upload — upload a new template
    └── admin/
        └── +page.svelte        # /admin — template metadata management
```

### Routing

| Path                   | Description                                                   |
| ---------------------- | ------------------------------------------------------------- |
| `/`                    | Browse template gallery, select a template to create a meme   |
| `/templates`           | My templates (created by the logged-in user)                  |
| `/templates/<id>`      | Meme editor — load template, add layers, download             |
| `/templates/<id>/edit` | Template editor — edit name, keywords, default text layers    |
| `/upload`              | Upload a new template image and configure default text layers |
| `/admin`               | Admin panel — manage all templates                            |

### State flow

```console
/ (+page.svelte)
  user selects template
    → editor.setTemplate(template)   ← store in editor.svelte.ts
    → goto('/templates/<id>')

/templates/<id> (+page.svelte)
  reads editor.template, editor.textLayers, editor.imageLayers …
  mutations go through editor.addTextLayer(), editor.updateTextLayer() …
```

The editor store is a module-level singleton that survives client-side navigation. On a hard refresh of `/templates/<id>`, the page fetches the template from the API directly.

### Auth store

`auth.svelte.ts` exposes a tri-state `auth.user`:

- `undefined` — initial state, `/auth/me` not yet called (shows loading)
- `null` — user is not logged in
- `User` — user is authenticated

`auth.init()` is called once in the root layout. Subsequent page navigations use the cached value.

### Checks and formatting

```bash
cd frontend
just format    # Prettier
just checks    # ESLint
```

---

## just targets (quick reference)

Run `just` in any directory to see available targets.

| Directory   | Target                    | What it does                                |
| ----------- | ------------------------- | ------------------------------------------- |
| root        | `just install-dev`        | Install backend + frontend dependencies     |
| root        | `just format`             | Format all code                             |
| root        | `just dev-up`             | Start full stack via Docker Compose         |
| root        | `just run-keycloak`       | Start ephemeral Keycloak container          |
| `backend/`  | `just run-dev`            | Start API server with hot reload            |
| `backend/`  | `just migrate`            | Apply pending DB migrations                 |
| `backend/`  | `just new-migrate name=x` | Generate a new migration from model changes |
| `backend/`  | `just checks`             | ty + ruff + bandit                          |
| `frontend/` | `just run-dev`            | Start Vite dev server                       |
| `frontend/` | `just checks`             | ESLint                                      |

---

## Documentation index

| File                              | Contents                                                 |
| --------------------------------- | -------------------------------------------------------- |
| [docs/dev.md](dev.md)             | This file — architecture and getting started             |
| [docs/env.md](env.md)             | All environment variables, defaults, and example configs |
| [docs/admin.md](admin.md)         | Admin panel user guide                                   |
| `http://localhost:8000/api/docs`  | Auto-generated OpenAPI / Swagger UI (backend running)    |
| `http://localhost:8000/api/redoc` | ReDoc alternative API docs                               |
