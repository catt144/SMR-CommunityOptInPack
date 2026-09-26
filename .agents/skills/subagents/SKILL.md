---
name: subagents
description: Launch a subagent in the Relaunched Fix Pack repo — which model tier and effort it gets, the owner-approval limits, how to brief it and how to check its result. Use before launching any subagent.
---

# Subagents

Delegate when a subagent does the work for less than it would cost in your own context. This
skill decides who does it, at what effort, and how you hand it over and take it back.

## Tiers

Find your own tier from your model name.

| tier | Claude | Codex | give it |
|---|---|---|---|
| 1 | Sonnet | Terra | well-instructed work: doc work, scripted reads, a pre-planned build, a simple, well-specified investigation. It reasons, but less deeply. |
| 2 | Opus | Sol | work that needs depth: investigation, judgement, a design-sensitive build |
| 3 | Fable | Astra | only work where a tier-2 result would have to be redone |

Haiku and Codex Luna are not used: they reason too lightly, and their context is far smaller than
the 1M of tiers 1-3.

## Limits (owner, 2026-09-18)

- Give each subagent the lowest tier that can do its task.
- Do not launch a subagent above your own tier without the owner's approval.
- Effort caps: tier 1 `xhigh`, tier 2 `high`, tier 3 `high`. Going above a cap needs the owner's
  express approval.
- Ask for approval with a justification: what the task needs that the lower tier or effort cannot
  give.
- Set effort explicitly. Left unset, a subagent inherits your session's effort in both Claude Code
  and Codex, which can exceed its cap.

## Setting model and effort

- **Claude Code:** launch one of the `.claude/agents/` types, which pin model and effort:
  `tier1-medium`, `tier1-high`, `tier1-xhigh` (Sonnet); `tier2-low`, `tier2-medium`, `tier2-high`
  (Opus); `tier3-medium`, `tier3-high` (Fable). They are local to this machine. A built-in type
  (general-purpose, Explore, Plan) or a bare model choice inherits the session's effort; use one
  only when that effort is within the subagent's cap.
- **Codex:** set `model` and `model_reasoning_effort` in a custom agent file (`.codex/agents/*.toml`
  for the project, `~/.codex/agents/` for personal), or on the spawn request. A file's values take
  precedence; `[agents] default_subagent_reasoning_effort` in `config.toml` is the fallback; unset,
  the subagent inherits the parent's. Source: developers.openai.com/codex/subagents (read
  2026-09-18).

## The brief

- The task alone: what to do, which files, what done looks like. The big picture, including the
  repo's gates, stays with you.
- The subagent does not run doccheck or the hooks, and runs no writing git command. You regenerate,
  run doccheck and commit. A task that changes a gate may run that gate.
- Parallel subagents get disjoint files, one writer per file.
- Ask for what its commands printed and for what it did not do.

## The result

Clear it with one check aimed at what it rests on (the trust rule in `CLAUDE.md`); do not redo the
work. Its explanations of machinery outside its task, such as why a gate went RED or what an exit
code meant, are the weak part: diagnose those yourself.
