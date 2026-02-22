from pathlib import Path

import pytest

from deployer import load_contract, main


def write_contract(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_load_contract_image_source(tmp_path: Path) -> None:
    file_path = write_contract(
        tmp_path / "app.yaml",
        """
name: sample-web
image: nginx:stable
type: web
replicas: 2
port: 80
""".strip(),
    )
    contract = load_contract(file_path)
    assert contract.name == "sample-web"
    assert contract.image == "nginx:stable"
    assert contract.git_repo is None
    assert contract.constraints == ["node.labels.role==general"]


def test_load_contract_ai_source_adds_ai_constraint(tmp_path: Path) -> None:
    file_path = write_contract(
        tmp_path / "ai.yaml",
        """
name: ai-service
image: ollama/ollama:latest
type: ai
replicas: 1
""".strip(),
    )
    contract = load_contract(file_path)
    assert contract.constraints[0] == "node.labels.role==ai"


def test_load_contract_rejects_dual_sources(tmp_path: Path) -> None:
    file_path = write_contract(
        tmp_path / "bad.yaml",
        """
name: bad-app
image: nginx
git_repo: https://github.com/example/repo.git
""".strip(),
    )
    with pytest.raises(ValueError, match="exactly one source"):
        load_contract(file_path)


def test_main_dry_run_keeps_contract(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    contract_file = write_contract(
        tmp_path / "sample.yaml",
        """
name: dry-run-app
image: nginx:stable
type: general
replicas: 1
port: 80
""".strip(),
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "deployer.py",
            "--queue-dir",
            str(tmp_path),
            "--dry-run",
        ],
    )
    exit_code = main()
    assert exit_code == 0
    assert contract_file.exists()
