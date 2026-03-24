from importlib import import_module
from pathlib import Path

import pytest


@pytest.fixture
def autoresearch_src_root() -> Path:
    return Path(__file__).resolve().parents[2] / "src"


@pytest.fixture
def eval_package(monkeypatch: pytest.MonkeyPatch, autoresearch_src_root: Path):
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    return import_module("autoresearch.candlemcstickface")
