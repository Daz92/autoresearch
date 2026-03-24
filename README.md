# autoresearch (CandleMcStickFace evaluator)

This package now hosts the CandleMcStickFace v1 fixed-judge evaluation surfaces used to improve desk behavior safely through bounded screener-rules mutation and deterministic replay.

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

## Canonical desk-state ownership

Canonical ownership metadata lives in:

- `agents/candlemcstickface/data/schema-version.yaml`

v1 owner keys:

- `working_list`
- `screener_rules`
- `opportunity_queue`

All replay and evaluation inputs should be sourced from these canonical desk-owned surfaces.

## Quality admission states

Watcher artifact admission returns one of:

- `complete`
- `degraded`
- `insufficient`
- `invalid`

Use this status to decide whether a cycle is fully evaluable or should be held/invalidated.

## Mutation and judge outcomes

Mutation proposals are screened by `check_mutation_eligibility` and must stay within the allowlisted `screener_rules.rules.{idx}.{field}` path shape plus numeric feasibility bounds.

Judge outcomes are fixed to:

- `promote`
- `hold`
- `revert`
- `invalid`

No other outcome string should be introduced in downstream logic.

## Capability profile workflow

Canonical capability requirements:

- `agents/candlemcstickface/data/capability-profiles.yaml`
- `agents/candlemcstickface/data/source-coverage-matrix.yaml`

If you change agent instructions/requirements, update these two files first and keep AGENTS/TOOLS docs aligned.

## Verification commands

Run from repository root:

```bash
pytest autoresearch/tests/candlemcstickface -v
PYTHONPATH=autoresearch/src python -c "from autoresearch.candlemcstickface.judge import JudgeOutcome; print('ok')"
uv run --project autoresearch --extra dev python -m build
```

Expected:

- test suite passes
- import smoke prints `ok`
- sdist/wheel build succeeds
