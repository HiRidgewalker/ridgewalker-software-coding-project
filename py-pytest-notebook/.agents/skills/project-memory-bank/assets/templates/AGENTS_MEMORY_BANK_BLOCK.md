<!-- BEGIN PROJECT MEMORY BANK -->
# Project Memory Bank Instructions

This project uses a project-local Memory Bank in `memory-bank/`.

## Startup Rule

- At the start of any project task, if `memory-bank/` exists, read all six core files before planning or editing:
  - `memory-bank/projectbrief.md`
  - `memory-bank/productContext.md`
  - `memory-bank/activeContext.md`
  - `memory-bank/systemPatterns.md`
  - `memory-bank/techContext.md`
  - `memory-bank/progress.md`
- Treat `projectbrief.md` as the source of truth for project goals and scope.
- Treat `activeContext.md` and `progress.md` as the first places to check for current work state.

## Update Triggers

Update the Memory Bank when any of these happen:

- The user explicitly asks to update, sync, record, or remember project context.
- A change is made to implementation, configuration, tests, migrations, documentation structure, or project behavior.
- The user confirms product scope, architecture, technical choices, long-term preferences, or workflow decisions.
- A repeated project constraint, convention, known issue, or gotcha is discovered.
- A milestone is completed, a significant bug is fixed, a known issue is introduced, or the next-step plan changes.
- A long task is about to start, context may be compacted, or the conversation is ending with durable project information not yet recorded.

Do not update the Memory Bank for one-off Q&A, transient command output explanations, or preferences that only affect the current response.

## Update Rules

- Keep updates concise and factual.
- Preserve useful historical decisions; do not rewrite history just to make the files look cleaner.
- Update `activeContext.md` for current focus, recent changes, open questions, and next steps.
- Update `progress.md` for what works, what remains, known issues, and decision log entries.
- Update `systemPatterns.md` or `techContext.md` only when architecture, patterns, commands, dependencies, or environment constraints change.
- Do not write project-level memory to `~/.codex/memories/`.
<!-- END PROJECT MEMORY BANK -->
