# Claude workflow for superTrade

## Goal

Use Claude with minimal repeated context and minimal token waste.

## Core rule

Do not paste a long opener on every task.
The repo memory already contains the default behavior.

Persistent context is already stored in:

1. `CLAUDE.md`
2. `.claude/rules/*.md`
3. `.claude/skills/*/SKILL.md`

Your chat prompt should usually contain only the task.

## Use prompts this short

### Feature

```text
Implement order history filters.
```
