# autoresearch (CandleMcStickFace evaluator)

<<<<<<< Updated upstream
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
=======
`autoresearch` is being rebuilt as a package-based framework for improving **trading signal agents** before paper-trading handoff.

## v1 scope

Version 1 is intentionally narrow:

- one plugin family: **signal-agent**
- a **fixed judge** owned by the framework
- a **mutable plugin surface** where candidates only propose standardized signals
- a paper-trading **handoff boundary** into desk-owned execution contracts instead of live broker logic inside this repo

This repository now contains the v1 core framework contracts and boundaries for Tasks 2-7.

## Repository layout

```text
src/autoresearch/           Python package root for the new framework
tests/                      scaffold and framework tests
legacy/karpathy_seed/       archived Karpathy training seed and original docs
pyproject.toml              project metadata, src layout, pytest config
```

## Legacy seed archive

The original LLM training seed has been preserved under `legacy/karpathy_seed/`.

- legacy code: `legacy/karpathy_seed/prepare.py` and `legacy/karpathy_seed/train.py`
- original operator prompt: `legacy/karpathy_seed/program.md`
- original project context: `legacy/karpathy_seed/README.md`

Use that directory for historical reference only while the new trading framework is built under `src/`.

## Development setup

```bash
uv sync --extra dev
uv run --extra dev pytest tests/test_scaffold.py -v
uv run --extra dev pytest tests -v
uv run python -c "import autoresearch; print('ok')"
```

## Implemented framework surface

Implemented in `src/autoresearch/`:

- `contracts.py`: typed contracts for snapshots, signal proposals, metrics, promotion states, and paper handoff payloads
- `provenance.py`: strict time-order validation (`market`, `symbol`, `as_of`, `available_at`, provenance)
- `score.py`: versioned composite score policy (`v1`)
- `judge.py`: fixed promotion decisions (`advance`, `hold`, `reject`, `invalid`) with hard gates
- `registry.py`: JSONL run registry for candidate/versioned score auditability
- `run_brief.py`: human-authored run-brief model/loader
- `plugins/signal_agent/`: plugin family and separate market adapters for US equities and crypto
- `integrations/candlemcstickface.py`: paper handoff payload mapping into desk TradeIntent contract shape

The repo does **not** implement live trading. Promotion stops at the paper handoff boundary.

## Verification commands

```bash
uv run --extra dev pytest tests -v
uv run python -c "import autoresearch; print('ok')"
uv run python -m build
```
>>>>>>> Stashed changes
