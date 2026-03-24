from importlib import import_module
from pathlib import Path
from types import MappingProxyType

import pytest


def test_bundle_hash_is_stable_for_same_input(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    bundle = import_module("autoresearch.candlemcstickface.bundle")

    payload = {"a": 1, "nested": {"z": [1, 2, 3]}}

    bundle1 = bundle.build_bundle(payload)
    bundle2 = bundle.build_bundle(payload)

    assert bundle1.bundle_hash == bundle2.bundle_hash
    assert bundle1.payload_hash == bundle2.payload_hash


def test_bundle_hash_changes_when_payload_changes(
    monkeypatch, autoresearch_src_root: Path
) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    bundle = import_module("autoresearch.candlemcstickface.bundle")

    bundle1 = bundle.build_bundle({"a": 1})
    bundle2 = bundle.build_bundle({"a": 2})

    assert bundle1.bundle_hash != bundle2.bundle_hash
    assert bundle1.payload_hash != bundle2.payload_hash


def test_bundle_payload_is_immutable(monkeypatch, autoresearch_src_root: Path) -> None:
    monkeypatch.syspath_prepend(str(autoresearch_src_root))
    bundle = import_module("autoresearch.candlemcstickface.bundle")

    frozen = bundle.build_bundle({"nested": {"answer": 42}, "values": [1, 2]})

    with pytest.raises(TypeError):
        frozen.payload["new"] = "nope"

    nested = frozen.payload["nested"]
    assert isinstance(nested, MappingProxyType)

    values = frozen.payload["values"]
    assert isinstance(values, tuple)
