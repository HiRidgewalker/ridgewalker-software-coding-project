---
name: project-memory-bank
description: Use only when the user explicitly invokes $project-memory-bank or directly asks to initialize or repair a project's Memory Bank. Creates or completes a project-local memory-bank directory and AGENTS.md rules, without overwriting existing project memory.
---

# Project Memory Bank

## Overview

Initialize a project-local Memory Bank based on Cline's six-file structure, plus AGENTS.md instructions that make future Codex sessions read and maintain it. This skill is an explicit bootstrap tool; do not use it for ordinary project work, memory-bank discussion, or background updates unless the user invokes `$project-memory-bank` or directly asks for initialization/repair.

## Workflow

1. Resolve the target project directory.
   - Default to the current working directory.
   - If the user provides a path, use that path.
2. Run the initializer script:

```bash
python3 /path/to/project-memory-bank/scripts/init_project_memory_bank.py /path/to/project
```

3. Report the created, skipped, and warning items from the script output.

## What It Creates

- `memory-bank/projectbrief.md`
- `memory-bank/productContext.md`
- `memory-bank/activeContext.md`
- `memory-bank/systemPatterns.md`
- `memory-bank/techContext.md`
- `memory-bank/progress.md`
- A marked Project Memory Bank section in project-local `AGENTS.md`

## Safety Rules

- Never overwrite existing Memory Bank files.
- Never replace existing `AGENTS.md` content.
- If `AGENTS.md` already contains the Project Memory Bank marker block, leave it unchanged.
- If a partial/corrupt marker block is detected, warn and do not modify `AGENTS.md`.
- Do not write to `~/.codex/memories/` or any user-level memory location.

## Resources

- `scripts/init_project_memory_bank.py`: idempotent initializer.
- `assets/templates/memory-bank/`: Markdown templates for the six Memory Bank files.
- `assets/templates/AGENTS_MEMORY_BANK_BLOCK.md`: AGENTS.md rules block with update triggers.
