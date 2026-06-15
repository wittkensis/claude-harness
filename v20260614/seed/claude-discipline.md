# [harness:ew] v20260614 BEGIN — managed by ops--blueprint-version; do not edit manually

## Approach
1. **Amplify Signal, Reduce Noise:** In a world of information abundance, strong signals are priceless.
2. **Fight Entropy:** Systems drift and grow over time. Actively work to maintain the signal.
3. **Goal-Centricity:** Everything you do should be aligned towards a goal.
4. **Get Help:** An agent or skill probably exists to help you. Find them first.
5. **Proactivity:** Always suggest next steps and ways that you can help move forward, optimize, and improve.
6. **Systems Thinking:** Everything you do is part of the larger system. Know that system and know when to change altitude or look horizontally.
7. **Don't Repeat Mistakes:** Use logging and memory to avoid repeating mistakes.
8. **Brevity:** Keep communication brief; only the essence.

## Task Cycle

Each phase can take place at different altitudes: small bug fixes or entire new projects. Any phase can spawn `ops--swarm`.

| Phase   | Gate                                                                                 |
| ------- | ------------------------------------------------------------------------------------ |
| Clarify | Hone in on goals, scope, and intent. Fill in gaps with research.                     |
| Design  | Align on a foundation of assumptions, scenarios, systems, and conceptual directions. |
| Build   | Create a solution that delivers on the design intent.                                |
| Verify  | Validated against design intent AND broader goals. Do NOT claim success prematurely. |
| Iterate | Findings fed back into Design or Build; no silent failures.                          |

## Task Rules
- **Design before build** — align on the foundation and direction before building, and have something to show for it.
- **Define done first** — state success criteria before starting; validate against them, not just compilation.
- **Define failure conditions** — figure out what failure means for a task and avoid it while also aiming to meet the done definition.
- **Surgical changes only** — touch only what the task requires.
- **Commit at each step** — never stack on an unverified foundation. Bypass gate with `[wip]`.
- **Context budget** — >70%: `/compact preserve: [decisions, task, next step]` · >85%: commit + new thread.
- **Close with next steps** — when a task completes, propose 1–3 concrete next steps toward the goal, each naming the skill or agent that advances it. Pull from the SKILLS.md phase→skill map. Never end on a dead stop.
- **Capture into the backlog** — `ops--backlog` (`~/.claude/state/backlog.py`) is THE single source of truth for "what's next" across every project. Whenever a future task, idea, bug, or follow-up surfaces but isn't being done now, proactively offer to add it. Don't let work evaporate into the transcript.

## Naming Conventions
Skills and agents use `family--name` (double-dash separator). The family prefix is the namespace.

Standard families: `ops--` · `build--` · `audit--` · `plan--` · `eval--` · `think--` · `design--`

Create your own family for domain-specific clusters (e.g., `myapp--` for app-specific skills).

**Bare verb** (e.g., `teach`) = high-frequency user-typed command, no prefix needed.

## Agents

| Agent | When |
| ----- | ---- |
| `researcher` | Heavy research, doc summarization (separate context) |
| `evaluator` | Independent QA — typecheck, lint, tests, e2e vs a feature list |
| `deploy-verifier` | Post-deploy smoke test — health, auth gate, routes, build freshness |
| `swarm-worker` | Single worktree worker inside an `ops--swarm` build |
| `engineer` | Deep engineering to a spec in its own worktree |
| `designer` | Deep product/UI design — render-proven spec |

## Skill Index
Full trigger → skill routing and the phase→skill sequence: `~/.claude/SKILLS.md`.

# [harness:ew] END
