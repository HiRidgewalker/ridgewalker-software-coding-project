# Product Context

## Problem

- The project needs a clean, reproducible local environment for learning pytest.

## Users

- Project owner using VS Code and terminal workflows.

## User Experience Goals

- VS Code should automatically use the project-local Python interpreter.
- Tests should run through `uv` and pytest with minimal setup friction.

## Success Criteria

- `uv run python --version` reports Python 3.12.x.
- `uv run pytest --version` reports an installed pytest version.
