# MarketIntel Agent

This project has been initialized with GitHub `spec-kit` and configured for Codex on Windows PowerShell.

The project constitution is now defined in [`.specify/memory/constitution.md`](C:\Users\杨清榆\PycharmProjects\MarketIntel_Agent\.specify\memory\constitution.md) and is based on the MarketIntel Agent behavior charter you provided.

## Included Spec Kit Structure

- `.specify/`: workflow scripts, templates, and project memory
- `.agents/skills/`: Codex-usable `speckit-*` skills
- `AGENTS.md`: agent guidance entrypoint

## Recommended Workflow

Run the following skills in order inside Codex:

1. `$speckit-constitution`
2. `$speckit-specify`
3. `$speckit-plan`
4. `$speckit-tasks`
5. `$speckit-implement`

Optional helper skills:

- `$speckit-clarify`
- `$speckit-checklist`
- `$speckit-analyze`

## Notes

- The repository was initialized locally with `spec-kit v0.7.3`.
- `.uv-cache/` is ignored because it is only used for local `uv` package caching.
- The constitution enforces lawful public-source intelligence, explicit credibility handling, structured outputs, and role-bounded multi-agent workflows.
