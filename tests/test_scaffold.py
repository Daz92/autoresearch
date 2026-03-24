from pathlib import Path
import sys


def test_src_package_root_exists(repo_root: Path) -> None:
    assert (repo_root / "src/autoresearch/__init__.py").exists()


def test_package_imports(repo_root: Path) -> None:
    sys.path.insert(0, str(repo_root / "src"))
    autoresearch = __import__("autoresearch")

    assert autoresearch.__version__ == "0.1.0"


def test_legacy_seed_quarantined(repo_root: Path) -> None:
    legacy_root = repo_root / "legacy/karpathy_seed"

    for file_name in [
        "prepare.py",
        "train.py",
        "program.md",
        "analysis.ipynb",
        "progress.png",
        "README.md",
    ]:
        assert (legacy_root / file_name).exists()


def test_root_readme_points_to_framework_and_legacy_seed(repo_root: Path) -> None:
    readme = (repo_root / "README.md").read_text(encoding="utf-8")

    assert "signal-agent" in readme
    assert "fixed judge" in readme
    assert "legacy/karpathy_seed/" in readme
