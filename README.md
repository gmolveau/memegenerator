# meme-generator

A fullstack webapp meme generator.

The meme editor is only on the frontend. The backend serves the templates.

## Stack

- backend: fastapi
- frontend: svelte

## Getting started

<details>
<summary>Install uv</summary>

[uv](https://docs.astral.sh/uv/) is required to manage Python dependencies.

On macOS/Linux:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On Windows:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

</details>

<details>
<summary>Install pnpm</summary>

[pnpm](https://pnpm.io/) is required to manage frontend dependencies.

On macOS/Linux:

```sh
curl -fsSL https://get.pnpm.io/install.sh | sh -
```

On macOS :

```sh
brew install pnpm
```

On Windows:

```powershell
iwr https://get.pnpm.io/install.ps1 -useb | iex
```

Or via npm:

```sh
npm install -g pnpm
```

</details>

- `make install-dev`
- Open two terminals :

```bash
cd backend
make migrate
make run-dev
```

```bash
cd frontend
make run-dev
```
