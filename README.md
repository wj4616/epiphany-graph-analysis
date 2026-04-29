# epiphany-graph-analysis

A Graph-of-Thought reimplementation of `epiphany-analysis`. Takes an original text (Node A) and an analysis of that text (Node B), produces a fresh enhanced Node A plus rich cataloging artifacts via a 14-node signal-driven graph topology with parallel spawn nodes and inline role-switched blocks.

**Status:** v1.0.3 design approved. Implementation in progress.

**Design spec:** [docs/2026-04-29-design.md](docs/2026-04-29-design.md) — also at `~/docs/superpowers/specs/2026-04-29-epiphany-graph-analysis-design.md`.

**Implementation plan:** `~/docs/superpowers/plans/2026-04-29-epiphany-graph-analysis.md`.

## Quick Reference

See spec "Quick Reference" section for invocation, modes, artifacts, hard gates, verification battery.

## Usage (once built)

```
/epiphany-graph-analysis <node-a> [<node-b>] [--deep] [--quiet|--verbose]
```

## Precedents

- `~/.claude/skills/epiphany-analysis/` — v2.0.0 inline pipeline being replaced
- `~/.claude/skills/epiphany-graph-genius/` — graph topology pattern adopted

## Layout

- `SKILL.md` — orchestrator
- `graph.json` — topology source of truth (single source per spec rule)
- `graph.schema.json` — programmatic validator
- `modules/N*.md` — per-node protocols (14 files)
- `kb/*.md` — knowledge base (12 files)
- `scripts/` — session-init.sh, validate-graph.py, test-runner.sh
- `tests/` — fixtures + smoke/signal/hg/verification/regression/replay
