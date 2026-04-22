# Claude workflow for superTrade

## Goal
Use Claude with minimal repeated context and minimal token waste.

## Durable layers
1. `CLAUDE.md`
   - always-on repo memory
2. `.claude/rules/*.md`
   - scoped coding rules by surface
3. `.claude/skills/*/SKILL.md`
   - repeatable procedures
4. task prompt
   - only the delta for the current task

## Recommended task opener
Use prompts like:

```text
Read CLAUDE.md and the relevant scoped rules first.
Then inspect the current code before proposing changes.

Task:
<your task>

Constraints:
- preserve API contracts unless explicitly changing them
- keep paper trading as default unless task says otherwise
- minimal diff
- update types if contracts change
- report verification commands and outcomes
```

## Recommended architecture prompt

```text
Read CLAUDE.md, docker-compose.yml, backend/app/main.py, backend/app/api/v1/router.py,
frontend/package.json, frontend/src/App.tsx, frontend/src/utils/api.ts, and frontend/src/store/index.ts.

Return:
1. implemented current state
2. gaps vs README
3. target design
4. smallest migration sequence
5. open risks
```

## Recommended bug prompt

```text
Read CLAUDE.md and investigate this bug without patching first.
Prove the first divergent layer, then propose the smallest fix.
Report exact reproduction and verification commands.
```
