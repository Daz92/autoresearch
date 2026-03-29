import json
from pathlib import Path
import subprocess
import sys

import yaml


def test_evaluator_normalizes_raw_market_strategist_proposal_in_memory(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    proposal_path = tmp_path / "strategist-proposal.yaml"
    output_path = tmp_path / "evaluation-result.json"
    registry_path = tmp_path / "registry.json"
    resume_state_path = tmp_path / "autoresearch-resume-state.json"

    proposal = {
        "proposal_id": "strategist-raw-1",
        "generated_at": "2026-03-29T12:00:00Z",
        "agent": "market-strategist",
        "sources": [],
        "presets": [
            {
                "name": "Momentum (medium-term trend)",
                "rationale": "Tighten liquidity floor.",
                "min_market_cap": 3000000000,
                "max_results": 12,
                "conditions": [
                    {"type": "price_change", "period": "60d", "min_pct": 12},
                    {"type": "price_change", "period": "20d", "min_pct": 6},
                    {"type": "rel_volume", "threshold": 1.3},
                ],
            }
        ],
    }
    proposal_path.write_text(
        yaml.safe_dump(proposal, sort_keys=False), encoding="utf-8"
    )

    command = [
        sys.executable,
        str(repo_root / "skills/autoresearch/scripts/evaluate_candlemcstickface.py"),
        "--proposal-file",
        str(proposal_path),
        "--resume-state-path",
        str(resume_state_path),
        "--registry-path",
        str(registry_path),
        "--output",
        str(output_path),
        "--bundle-payload-file",
        str(
            repo_root / "skills/autoresearch/evals/fixtures/frozen-bundle-payload.json"
        ),
        "--baseline-metrics-file",
        str(repo_root / "skills/autoresearch/evals/fixtures/baseline-metrics.json"),
        "--mutant-metrics-file",
        str(repo_root / "skills/autoresearch/evals/fixtures/mutant-metrics.json"),
        "--holdout-metrics-file",
        str(repo_root / "skills/autoresearch/evals/fixtures/holdout-metrics.json"),
    ]

    result = subprocess.run(command, cwd=repo_root, capture_output=True, text=True)

    assert result.returncode == 0, result.stderr

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["proposal"]["changes"] == {
        "screener_rules.rules.0.rationale": "Tighten liquidity floor.",
        "screener_rules.rules.0.min_market_cap": 3000000000,
        "screener_rules.rules.0.max_results": 12,
    }
    assert payload["judge"]["outcome"] == "promote"
    assert resume_state_path.exists()
    assert not (
        repo_root / "agents/candlemcstickface/data/normalized-strategist-proposal.yaml"
    ).exists()

    resume_state = json.loads(resume_state_path.read_text(encoding="utf-8"))
    assert resume_state["proposal_id"] == "strategist-raw-1"
    assert resume_state["stage"] == "evaluated"
    assert resume_state["outcome"] == "promote"
