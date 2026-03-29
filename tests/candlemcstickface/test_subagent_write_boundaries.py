from pathlib import Path
import importlib.util
import subprocess
import sys

import yaml


def test_forbidden_subagent_artifact_paths_are_absent() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    forbidden_paths = [
        "agents/watcher/temp",
        "agents/watcher/tmp",
        "agents/watcher/output",
        "agents/watcher/reports",
        "agents/watcher/temp_analysis.py",
        "agents/watcher/crypto_monitoring_report.yaml",
        "agents/watcher/watcher_report_20260325_095033.yaml",
        "agents/watcher/data/monitor_results.json",
    ]

    for rel_path in forbidden_paths:
        assert not (repo_root / rel_path).exists(), rel_path


def test_run_screener_evaluates_canonical_rules_schema() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    module_path = repo_root / "agents/stock-scanner/run_screener.py"
    spec = importlib.util.spec_from_file_location("run_screener_module", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    rules = yaml.safe_load(
        (repo_root / "agents/candlemcstickface/data/screener-rules.yaml").read_text(
            encoding="utf-8"
        )
    )
    momentum_rule = rules["rules"][0]

    bars = []
    for index in range(61):
        close = 100.0 + index
        bars.append(
            {
                "date": f"2026-01-{index + 1:02d}",
                "open": close - 0.5,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 2_500_000.0 if index == 60 else 1_000_000.0,
            }
        )

    candidate = module.evaluate_rule(
        momentum_rule,
        symbol="TEST",
        bars=bars,
        metadata={"market_cap": 3_000_000_000.0, "beta": 0.8},
    )

    assert candidate is not None
    assert candidate["symbol"] == "TEST"
    assert candidate["setup"] == "Momentum (medium-term trend)"
    assert candidate["conviction"] in {"medium", "high"}


def test_queue_writer_behavior_is_canonical() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    run_screener = repo_root / "agents/stock-scanner/run_screener.py"
    run_task_screener = repo_root / "agents/stock-scanner/run_task_screener.py"
    deprecated_scripts = [
        repo_root / "agents/stock-scanner/analyze_scan.py",
        repo_root / "agents/stock-scanner/analyze_screener.py",
        repo_root / "agents/stock-scanner/screening/comprehensive_screening.py",
        repo_root / "agents/stock-scanner/scripts/screener_engine.py",
    ]

    dry_run_output = repo_root / ".tmp" / "tests" / "canonical-queue.yaml"
    delegated_output = repo_root / ".tmp" / "tests" / "delegated-queue.yaml"
    dry_run_output.parent.mkdir(parents=True, exist_ok=True)
    if dry_run_output.exists():
        dry_run_output.unlink()
    if delegated_output.exists():
        delegated_output.unlink()

    direct = subprocess.run(
        [
            sys.executable,
            str(run_screener),
            "--dry-run",
            "--output",
            str(dry_run_output),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert direct.returncode == 0, direct.stderr
    assert dry_run_output.exists()
    direct_payload = yaml.safe_load(dry_run_output.read_text(encoding="utf-8"))
    assert direct_payload["agent"] == "stock-scanner"

    delegated = subprocess.run(
        [
            sys.executable,
            str(run_task_screener),
            "--dry-run",
            "--output",
            str(delegated_output),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert delegated.returncode == 0, delegated.stderr
    assert delegated_output.exists()

    for script_path in deprecated_scripts:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "Deprecated: use agents/stock-scanner/run_screener.py" in (
            result.stderr or result.stdout
        )
