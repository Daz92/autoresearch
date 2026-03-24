# autoresearch (CandleMcStickFace evaluator)

`autoresearch` is the workspace framework for improving CandleMcStickFace safely through bounded screener-rules mutation, deterministic replay, and fixed judge outcomes.

## What is implemented

The `autoresearch.candlemcstickface` package currently includes:

- Canonical contracts (`contracts.py`)
- Canonical desk-state metadata loader (`canonical_state.py`)
- Capability profile loader (`capability_profiles.py`)
- Quality admission gates (`admission.py`)
- Mutation eligibility gate for screener-rules proposals (`mutation_gate.py`)
- Immutable desk-cycle bundle assembly (`bundle.py`)
- Deterministic replay surface (`replay.py`)
- Fixed judge and outcomes (`judge.py`)
- Append-only registry API (`registry.py`)
- Paper handoff adapter (`integrations/candlemcstickface.py`)

## Scope

Version 1 is intentionally narrow:

- one desk integration: **CandleMcStickFace**
- a **fixed judge** owned by the framework
- a bounded mutation surface where candidates only change allowlisted screener-rules fields
- a paper-trading handoff boundary instead of live broker logic inside this package

The repo does **not** implement live trading. Promotion stops at the desk-owned handoff boundary.

## Canonical desk-state ownership

Canonical ownership metadata lives in:

- `agents/candlemcstickface/data/schema-version.yaml`

Current owner keys:

- `working_list`
- `screener_rules`
- `opportunity_queue`

All replay and evaluation inputs should be sourced from these canonical desk-owned surfaces.

## Capability profile workflow

Canonical capability requirements:

- `agents/candlemcstickface/data/capability-profiles.yaml`
- `agents/candlemcstickface/data/source-coverage-matrix.yaml`

If you change agent requirements or desk-side evaluation policy, update those files first and keep the AGENTS/TOOLS docs aligned.

## Quality admission states

Watcher artifact admission returns one of:

- `complete`
- `degraded`
- `insufficient`
- `invalid`

Use this status to decide whether a cycle is fully evaluable or should be held or invalidated.

## Mutation and judge outcomes

Mutation proposals are screened by `check_mutation_eligibility` and must stay within the allowlisted `screener_rules.rules.{idx}.{field}` path shape plus numeric feasibility bounds.

Judge outcomes are fixed to:

- `promote`
- `hold`
- `revert`
- `invalid`

No downstream layer should invent extra outcome strings.

## Repository layout

```text
src/autoresearch/           Python package root for the framework
tests/                      framework and desk integration tests
legacy/karpathy_seed/       archived Karpathy training seed and original docs
pyproject.toml              project metadata and test/build configuration
```

## Verification commands

Run from the workspace root:

```bash
uv run --project autoresearch --extra dev pytest autoresearch/tests/candlemcstickface -v
PYTHONPATH=autoresearch/src python -c "from autoresearch.candlemcstickface.judge import JudgeOutcome; print('ok')"
uv run --project autoresearch --extra dev python -m build
```

Expected:

- desk evaluator test suite passes
- import smoke prints `ok`
- sdist/wheel build succeeds
