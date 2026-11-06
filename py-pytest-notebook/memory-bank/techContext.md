# Tech Context

## Stack

- Python 3.12
- pytest
- uv

## Environment

- Project virtual environment: `.venv`
- VS Code interpreter: `${workspaceFolder}/.venv/bin/python`

## Commands

- Build: not currently applicable
- Test: `uv run pytest`
- Run: `uv run python`

## Dependencies

- Development dependency: `pytest>=9.1.0`

## Technical Constraints

- `pyproject.toml` restricts Python to `>=3.12,<3.13`.
- Use `UV_CACHE_DIR=/tmp/uv-cache` in this sandbox if `uv` cannot write to the default user cache.
