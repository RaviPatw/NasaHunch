#!/usr/bin/env python3
"""
Generic application deployer for NASA HUNCH Raspberry Pi server farm.

Features:
- Reads queued YAML contracts.
- Supports either a Docker image or Git repo with Dockerfile.
- Applies AI/general node placement constraints.
- Supports env vars, resources, command/args, and port publishing.
- Dry-run mode for safe validation tests.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import yaml


SERVICE_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{1,62}$")


@dataclass
class Contract:
    name: str
    app_type: str
    replicas: int
    image: Optional[str]
    git_repo: Optional[str]
    git_ref: Optional[str]
    dockerfile: str
    build_context: str
    port: Optional[int]
    publish_port: Optional[int]
    env: Dict[str, str]
    constraints: List[str]
    cpu_limit: Optional[str]
    memory_limit: Optional[str]
    command: Optional[str]
    args: List[str]
    network: Optional[str]


def run(cmd: List[str], dry_run: bool = False, cwd: Optional[Path] = None) -> None:
    rendered = " ".join(cmd)
    if dry_run:
        print(f"[DRY RUN] {rendered}")
        return
    print(f"[RUN] {rendered}")
    subprocess.run(cmd, check=True, cwd=str(cwd) if cwd else None)


def load_contract(path: Path) -> Contract:
    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    if not isinstance(raw, dict):
        raise ValueError("Contract root must be a YAML mapping/object.")

    name = str(raw.get("name", "")).strip()
    if not SERVICE_NAME_PATTERN.match(name):
        raise ValueError(
            "Invalid 'name'. Use 2-63 chars: lowercase letters, numbers, '_' or '-', "
            "and start with a letter/number."
        )

    app_type = str(raw.get("type", "general")).strip().lower()
    replicas = int(raw.get("replicas", 1))
    if replicas < 1:
        raise ValueError("'replicas' must be >= 1.")

    image = _clean_optional(raw.get("image"))
    git_repo = _clean_optional(raw.get("git_repo"))
    if bool(image) == bool(git_repo):
        raise ValueError("Provide exactly one source: 'image' or 'git_repo'.")

    git_ref = _clean_optional(raw.get("git_ref"))
    dockerfile = str(raw.get("dockerfile", "Dockerfile")).strip()
    build_context = str(raw.get("build_context", ".")).strip()

    port = _parse_optional_port(raw.get("port"))
    publish_port = _parse_optional_port(raw.get("publish_port"))

    env = raw.get("env", {})
    if env is None:
        env = {}
    if not isinstance(env, dict):
        raise ValueError("'env' must be a mapping of KEY: VALUE.")
    env = {str(k): str(v) for k, v in env.items()}

    cpu_limit = _clean_optional(raw.get("cpu_limit"))
    memory_limit = _clean_optional(raw.get("memory_limit"))
    command = _clean_optional(raw.get("command"))

    args = raw.get("args", [])
    if args is None:
        args = []
    if not isinstance(args, list):
        raise ValueError("'args' must be a list.")
    args = [str(item) for item in args]

    network = _clean_optional(raw.get("network"))

    constraints = _build_constraints(app_type, raw.get("constraints"))

    return Contract(
        name=name,
        app_type=app_type,
        replicas=replicas,
        image=image,
        git_repo=git_repo,
        git_ref=git_ref,
        dockerfile=dockerfile,
        build_context=build_context,
        port=port,
        publish_port=publish_port,
        env=env,
        constraints=constraints,
        cpu_limit=cpu_limit,
        memory_limit=memory_limit,
        command=command,
        args=args,
        network=network,
    )


def _clean_optional(value: object) -> Optional[str]:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _parse_optional_port(value: object) -> Optional[int]:
    if value is None:
        return None
    port = int(value)
    if port < 1 or port > 65535:
        raise ValueError("Ports must be in range 1..65535.")
    return port


def _build_constraints(app_type: str, raw_constraints: object) -> List[str]:
    constraints: List[str] = []
    if app_type == "ai":
        constraints.append("node.labels.role==ai")
    else:
        constraints.append("node.labels.role==general")

    if raw_constraints is None:
        return constraints
    if not isinstance(raw_constraints, list):
        raise ValueError("'constraints' must be a list of swarm constraints.")
    constraints.extend(str(item).strip() for item in raw_constraints if str(item).strip())
    return constraints


def resolve_image(contract: Contract, dry_run: bool = False) -> str:
    if contract.image:
        return contract.image

    assert contract.git_repo is not None
    image_tag = f"{contract.name}:queued"
    with tempfile.TemporaryDirectory(prefix="nasa_hunch_") as tmp:
        repo_path = Path(tmp) / "repo"
        cmd = ["git", "clone", "--depth", "1"]
        if contract.git_ref:
            cmd.extend(["--branch", contract.git_ref])
        cmd.extend([contract.git_repo, str(repo_path)])
        run(cmd, dry_run=dry_run)

        context_dir = (repo_path / contract.build_context).resolve()
        if not dry_run and not context_dir.exists():
            raise ValueError(
                f"Build context '{contract.build_context}' not found in repository."
            )

        dockerfile = context_dir / contract.dockerfile
        if not dry_run and not dockerfile.exists():
            raise ValueError(f"Dockerfile '{contract.dockerfile}' not found in build context.")

        run(
            [
                "docker",
                "build",
                "-f",
                str(dockerfile),
                "-t",
                image_tag,
                str(context_dir),
            ],
            dry_run=dry_run,
        )
    return image_tag


def deploy_contract(
    path: Path,
    contract: Contract,
    dry_run: bool = False,
    remove_contract_on_success: bool = True,
) -> None:
    image_ref = resolve_image(contract, dry_run=dry_run)

    cmd = [
        "docker",
        "service",
        "create",
        "--name",
        contract.name,
        "--replicas",
        str(contract.replicas),
    ]

    for item in contract.constraints:
        cmd.extend(["--constraint", item])

    if contract.network:
        cmd.extend(["--network", contract.network])

    if contract.port:
        published = contract.publish_port if contract.publish_port else 0
        cmd.extend(["--publish", f"published={published},target={contract.port}"])

    if contract.cpu_limit:
        cmd.extend(["--limit-cpu", contract.cpu_limit])
    if contract.memory_limit:
        cmd.extend(["--limit-memory", contract.memory_limit])

    for key, value in contract.env.items():
        cmd.extend(["--env", f"{key}={value}"])

    cmd.append(image_ref)
    if contract.command:
        cmd.append(contract.command)
    cmd.extend(contract.args)

    run(cmd, dry_run=dry_run)

    if dry_run:
        print(f"[DRY RUN] contract validated: {path.name}")
    elif remove_contract_on_success:
        path.unlink()
    print(f"[OK] deployment complete: {contract.name}")


def iter_contracts(queue_dir: Path, single_file: Optional[Path]) -> Iterable[Path]:
    if single_file:
        if not single_file.exists():
            raise FileNotFoundError(f"Contract not found: {single_file}")
        return [single_file]
    contracts = sorted(queue_dir.glob("*.yaml")) + sorted(queue_dir.glob("*.yml"))
    return contracts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deploy queued application contracts to Docker Swarm.")
    parser.add_argument(
        "--queue-dir",
        default=str((Path(__file__).resolve().parent.parent / "queue")),
        help="Directory containing app contracts (*.yaml/*.yml).",
    )
    parser.add_argument(
        "--file",
        default=None,
        help="Deploy only this contract file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print docker commands without deploying.",
    )
    parser.add_argument(
        "--keep-contract",
        action="store_true",
        help="Do not remove contract file after successful deployment.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    queue_dir = Path(args.queue_dir).resolve()
    single_file = Path(args.file).resolve() if args.file else None

    if not queue_dir.exists() and not single_file:
        print(f"Queue directory not found: {queue_dir}", file=sys.stderr)
        return 1

    contracts = list(iter_contracts(queue_dir, single_file))
    if not contracts:
        print("No applications waiting to deploy.")
        return 0

    failed = False
    for contract_path in contracts:
        print(f"[INFO] processing: {contract_path}")
        try:
            contract = load_contract(contract_path)
            deploy_contract(
                contract_path,
                contract,
                dry_run=args.dry_run,
                remove_contract_on_success=not args.keep_contract,
            )
            if args.keep_contract and not args.dry_run and contract_path.exists():
                print(f"[INFO] contract retained: {contract_path.name}")
        except Exception as exc:  # pragma: no cover - failure path is tested via return code.
            failed = True
            print(f"[ERROR] {contract_path.name}: {exc}", file=sys.stderr)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
