# Instructions for agents

- Use `just --list` to find available development targets
- Before committing `.py` changes, run `just format` to format
- Don't edit `pyproject.toml` directly, use `uv add` or `uv add -dev` to add dependencies
- Don't edit `package.json` directly, use `pnpm add` to add dependencies
- Before committing `.ts` `html` `.svelte` changes, run `just format` to lint
