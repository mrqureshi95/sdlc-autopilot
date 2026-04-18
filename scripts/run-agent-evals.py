#!/usr/bin/env python3
"""Machine-checkable harness for SDLC Autopilot agent eval runs.

Expected run artifact layout:

  <runs-dir>/
    2-simple-bug-fix/
      meta.json
      patch.diff
      transcript.md  # optional

Core behavior:
- Copies the fixture to a temporary workspace
- Initializes git and commits the base fixture
- Copies verifier scripts into the temp workspace
- Optionally installs JS deps for npm fixtures
- Applies the agent patch
- Runs verify-pipeline.sh using the mode declared in meta.json
- Evaluates optional machine_checks declared in evals.json

This does not prove every assertion, but it upgrades evals from pure fixture
validation to repeatable, machine-checked artifact evaluation.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any


MODE_VALUES = {"quick", "standard", "full"}


def run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), env=env, text=True, capture_output=True)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def find_run_dir(runs_dir: Path, eval_case: dict[str, Any]) -> Path | None:
    candidates = [
        runs_dir / f"{eval_case['id']}-{eval_case['name']}",
        runs_dir / str(eval_case["id"]),
        runs_dir / eval_case["name"],
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def ensure_git_repo(workdir: Path) -> None:
    run(["git", "init", "-q"], cwd=workdir)
    run(["git", "config", "user.email", "evals@sdlc-autopilot.local"], cwd=workdir)
    run(["git", "config", "user.name", "SDLC Eval Harness"], cwd=workdir)
    run(["git", "add", "."], cwd=workdir)
    commit = run(["git", "commit", "-q", "-m", "base fixture"], cwd=workdir)
    if commit.returncode != 0:
        raise RuntimeError(commit.stderr or commit.stdout or "failed to create base fixture commit")


def prepare_workspace(repo_root: Path, fixture_dir: Path) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="sdlc-agent-eval-"))
    workdir = temp_dir / "workspace"
    shutil.copytree(fixture_dir, workdir)

    scripts_dir = workdir / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    for script_name in ("verify-pipeline.sh", "verify-inversion.sh"):
        shutil.copy2(repo_root / "scripts" / script_name, scripts_dir / script_name)

    ensure_git_repo(workdir)
    maybe_install_dependencies(workdir)
    return workdir


def maybe_install_dependencies(workdir: Path) -> None:
    package_json = workdir / "package.json"
    if package_json.exists():
        install = run(["npm", "install", "--no-fund", "--no-audit"], cwd=workdir)
        if install.returncode != 0:
            raise RuntimeError(install.stderr or install.stdout or "npm install failed")


def apply_patch_file(workdir: Path, patch_path: Path) -> None:
    applied = run(["git", "apply", "--whitespace=nowarn", str(patch_path)], cwd=workdir)
    if applied.returncode != 0:
        raise RuntimeError(applied.stderr or applied.stdout or "failed to apply patch")


def validate_meta(eval_case: dict[str, Any], meta: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if meta.get("eval_id") != eval_case["id"]:
        errors.append(f"meta.eval_id={meta.get('eval_id')} does not match eval id {eval_case['id']}")
    if meta.get("mode") not in MODE_VALUES:
        errors.append(f"meta.mode must be one of {sorted(MODE_VALUES)}")
    elif meta["mode"] != eval_case["expected_mode"]:
        errors.append(f"meta.mode={meta['mode']} does not match expected_mode={eval_case['expected_mode']}")
    return errors


def execute_machine_check(check: dict[str, Any], meta: dict[str, Any], transcript: str, diff_text: str, changed_files: set[str]) -> tuple[bool, str]:
    check_type = check.get("type")
    if check_type == "meta_flag":
        flag = check["value"]
        flags = set(meta.get("flags", []))
        return (flag in flags, f"meta flag '{flag}' {'present' if flag in flags else 'missing'}")
    if check_type == "meta_summary_contains":
        value = check["value"]
        summary = meta.get("summary", "")
        return (value in summary, f"summary contains '{value}'" if value in summary else f"summary missing '{value}'")
    if check_type == "transcript_contains":
        value = check["value"]
        return (value in transcript, f"transcript contains '{value}'" if value in transcript else f"transcript missing '{value}'")
    if check_type == "diff_contains":
        value = check["value"]
        return (value in diff_text, f"diff contains '{value}'" if value in diff_text else f"diff missing '{value}'")
    if check_type == "diff_not_contains":
        value = check["value"]
        return (value not in diff_text, f"diff omits '{value}'" if value not in diff_text else f"diff unexpectedly contains '{value}'")
    if check_type == "changed_file_contains":
        value = check["value"]
        matched = any(value in item for item in changed_files)
        return (matched, f"changed file contains '{value}'" if matched else f"no changed file contains '{value}'")
    if check_type == "verify_output_contains":
        value = check["value"]
        verify_output = meta.get("verify_output", "")
        return (value in verify_output, f"verify output contains '{value}'" if value in verify_output else f"verify output missing '{value}'")
    if check_type == "transcript_not_contains":
        value = check["value"]
        return (value not in transcript, f"transcript omits '{value}'" if value not in transcript else f"transcript unexpectedly contains '{value}'")
    if check_type == "file_contains":
        relative_path = check["path"]
        value = check["value"]
        content = meta.get("workspace_files", {}).get(relative_path, "")
        return (value in content, f"{relative_path} contains '{value}'" if value in content else f"{relative_path} missing '{value}'")
    return (False, f"unsupported machine check type '{check_type}'")


def evaluate_case(repo_root: Path, eval_case: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    meta_path = run_dir / "meta.json"
    patch_path = run_dir / "patch.diff"
    transcript_path = run_dir / "transcript.md"

    result: dict[str, Any] = {
        "id": eval_case["id"],
        "name": eval_case["name"],
        "status": "failed",
        "errors": [],
        "checks": [],
    }

    if not meta_path.exists():
      result["errors"].append("meta.json missing")
      return result
    if not patch_path.exists():
      result["errors"].append("patch.diff missing")
      return result

    meta = load_json(meta_path)
    result["meta"] = meta
    result["errors"].extend(validate_meta(eval_case, meta))
    if result["errors"]:
        return result

    fixture_dir = repo_root / "evals" / eval_case["fixture"]
    try:
        workdir = prepare_workspace(repo_root, fixture_dir)
        apply_patch_file(workdir, patch_path)
    except Exception as exc:  # noqa: BLE001
        result["errors"].append(str(exc))
        return result

    env = os.environ.copy()
    if meta.get("strict_inversion"):
        env["SDLC_STRICT_INVERSION"] = "1"
    if meta.get("inversion_base_ref"):
        env["SDLC_INVERSION_BASE_REF"] = str(meta["inversion_base_ref"])

    verify = run(["sh", "scripts/verify-pipeline.sh", meta["mode"]], cwd=workdir, env=env)
    result["verify_returncode"] = verify.returncode
    result["verify_output"] = (verify.stdout + verify.stderr).strip()
    meta["verify_output"] = result["verify_output"]
    if verify.returncode != 0:
        result["errors"].append("verify-pipeline.sh failed")

    transcript = transcript_path.read_text(encoding="utf-8") if transcript_path.exists() else ""
    diff_text = patch_path.read_text(encoding="utf-8")
    changed_files = {
        line.split()[-1].removeprefix("b/")
        for line in diff_text.splitlines()
        if line.startswith("diff --git ")
    }
    meta["workspace_files"] = {}
    for changed_file in changed_files:
        file_path = workdir / changed_file
        if file_path.exists() and file_path.is_file():
            meta["workspace_files"][changed_file] = file_path.read_text(encoding="utf-8")

    for check in eval_case.get("machine_checks", []):
        passed, message = execute_machine_check(check, meta, transcript, diff_text, changed_files)
        result["checks"].append({"check": check, "passed": passed, "message": message})
        if not passed:
            result["errors"].append(message)

    if not result["errors"]:
        result["status"] = "passed"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run machine-checkable SDLC agent evals")
    parser.add_argument("--runs-dir", required=True, help="Directory containing agent run artifacts")
    parser.add_argument("--eval-id", type=int, help="Run only one eval id")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    runs_dir = Path(args.runs_dir).resolve()
    evals = load_json(repo_root / "evals" / "evals.json")["evals"]

    selected = [case for case in evals if args.eval_id is None or case["id"] == args.eval_id]
    if not selected:
        print("No matching evals selected", file=sys.stderr)
        return 2

    summary: dict[str, Any] = {"passed": 0, "failed": 0, "results": []}

    for eval_case in selected:
        run_dir = find_run_dir(runs_dir, eval_case)
        if run_dir is None:
            summary["failed"] += 1
            summary["results"].append(
                {
                    "id": eval_case["id"],
                    "name": eval_case["name"],
                    "status": "failed",
                    "errors": ["run artifact directory not found"],
                    "checks": [],
                }
            )
            continue

        result = evaluate_case(repo_root, eval_case, run_dir)
        summary["results"].append(result)
        summary[result["status"]] += 1

    print(json.dumps(summary, indent=2))
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())