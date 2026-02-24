# Environment Variables

## Frontend

Configured via a `.env` file at `frontend/`.
Variables must be prefixed with `PUBLIC_` to be exposed to the browser (SvelteKit / Vite convention).

| Variable         | Default                 | Description                                                        |
| ---------------- | ----------------------- | ------------------------------------------------------------------ |
| `PUBLIC_API_URL` | `http://localhost:8000` | Base URL of the backend API. Used to build all API and image URLs. |

---

## Backend

Configured via a `.env` file at the repo root (e.g. copy `.env.dev.example`).

### Security / CORS

| Variable          | Default                    | Description                                                                     |
| ----------------- | -------------------------- | ------------------------------------------------------------------------------- |
| `ALLOWED_HOSTS`   | `localhost:5173,localhost` | Comma-separated list of allowed `Host` header values (`TrustedHostMiddleware`). |
| `ALLOWED_ORIGINS` | `http://localhost:5173`    | Comma-separated list of origins allowed by CORS.                                |

### Database

| Variable       | Default                              | Description                                                 |
| -------------- | ------------------------------------ | ----------------------------------------------------------- |
| `DATABASE_URL` | `sqlite:///./data/meme_generator.db` | SQLAlchemy connection URL. Defaults to a local SQLite file. |

### Storage

| Variable         | Default | Description                                             |
| ---------------- | ------- | ------------------------------------------------------- |
| `STORAGE_DRIVER` | `local` | Storage backend to use. Accepted values: `local`, `s3`. |

#### Local driver (`STORAGE_DRIVER=local`)

| Variable                 | Default             | Description                                                     |
| ------------------------ | ------------------- | --------------------------------------------------------------- |
| `STORAGE_LOCAL_PATH`     | `data/templates`    | Filesystem directory where uploaded template images are stored. |
| `STORAGE_LOCAL_BASE_URL` | `/static/templates` | URL prefix used to build public image URLs.                     |

#### S3 driver (`STORAGE_DRIVER=s3`)

| Variable                       | Default      | Required | Description                                                                             |
| ------------------------------ | ------------ | -------- | --------------------------------------------------------------------------------------- |
| `STORAGE_S3_BUCKET`            | —            | **Yes**  | S3 bucket name.                                                                         |
| `STORAGE_S3_REGION`            | `us-east-1`  | No       | AWS region (or equivalent for S3-compatible services).                                  |
| `STORAGE_S3_PREFIX`            | `templates/` | No       | Key prefix inside the bucket.                                                           |
| `STORAGE_S3_ENDPOINT_URL`      | —            | No       | Custom endpoint URL for S3-compatible services (MinIO, Cloudflare R2, …). Omit for AWS. |
| `STORAGE_S3_ACCESS_KEY_ID`     | —            | No       | Explicit AWS / S3-compatible access key. Can be omitted when using IAM roles.           |
| `STORAGE_S3_SECRET_ACCESS_KEY` | —            | No       | Explicit AWS / S3-compatible secret key. Can be omitted when using IAM roles.           |
