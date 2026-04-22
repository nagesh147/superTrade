# Claude workflow for superTrade

## Goal
Use Claude with minimal repeated context and minimal token waste.

## Memory model for this repo
Persistent context is already stored in:
1. `CLAUDE.md`
2. `.claude/rules/*.md`
3. `.claude/skills/*/SKILL.md`
4. Claude auto memory when enabled

Your chat prompt should usually contain only the task.

## Core rule
Do not paste a long opener on every task.
Do not keep retyping:
- read CLAUDE.md first
- inspect code first
- preserve contracts
- keep paper trading default
- use minimal diff
- report verification results

Those behaviors are already encoded in repo memory.

## Use prompts this short
### Feature
```text
Implement order history filters.
```

### Bug
```text
Fix WebSocket reconnect bug.
```

### Analysis
```text
Audit auth flow. No code yet.
```

### Refactor
```text
Refactor order service. No behavior change.
```

### End-to-end
```text
Add JWT refresh end-to-end.
```

## When to add extra words
Add extra constraints only when they are task-specific:
- `Implement PnL chart. Use existing dashboard cards only.`
- `Fix order placement bug. Backend only.`
- `Audit strategy engine. No code. Compare README vs implementation.`
- `Change order payload contract and update all consumers.`

## Project vs personal memory
### Shared in git
- `CLAUDE.md`
- `.claude/rules/`
- `.claude/skills/`
- `.claude/settings.json`

### Personal and usually gitignored
- `CLAUDE.local.md`
- `.claude/settings.local.json`

Use `CLAUDE.local.md` for machine-specific notes, private sandbox URLs, or local preferences that should not be committed.

## Auto memory
Auto memory should stay enabled for this repo unless you have a specific reason to disable it.
It is useful for:
- build/debugging insights
- repeated local workflow corrections
- repo-specific gotchas discovered over time

Open `/memory` in Claude Code to:
- inspect loaded memory files
- verify which CLAUDE files are active
- browse or edit auto memory

## Path-scoped rules
This repo uses `.claude/rules/` with file-path scoping.
That keeps backend, frontend, and infrastructure instructions out of the context window unless Claude is working in those areas.

## Repo-specific environment note
The current backend dependency pins are safest on Python 3.12.
If Claude suggests using system `pip` or Python 3.14 for backend setup, override that suggestion.
Use `backend/.venv` with Python 3.12 instead.

## Mental model
```text
Permanent context = repo files
Task prompt       = current delta only
```

## Anti-pattern
This usually wastes tokens and should not be pasted repeatedly:

```text
Read CLAUDE.md and the relevant scoped rules first.
Then inspect the current code before proposing changes.

Task:
<your task>

Constraints:
- preserve API contracts unless explicitly changing them
- keep paper trading as default unless task says otherwise
- minimal diff
- update backend, frontend, and types together if contracts change
- report exact verification commands and outcomes
```
