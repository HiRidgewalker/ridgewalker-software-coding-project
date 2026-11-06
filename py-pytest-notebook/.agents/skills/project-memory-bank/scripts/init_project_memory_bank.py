#!/usr/bin/env python3
"""Initialize a project-local Memory Bank without overwriting existing files."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


BEGIN_MARKER = "<!-- BEGIN PROJECT MEMORY BANK -->"
END_MARKER = "<!-- END PROJECT MEMORY BANK -->"


@dataclass
class Result:
    created: list[str]
    skipped: list[str]
    warnings: list[str]


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_asset(relative_path: str) -> str:
    return (skill_root() / "assets" / "templates" / relative_path).read_text(
        encoding="utf-8"
    )


def write_if_missing(
    target_root: Path, relative_path: str, content: str, result: Result, dry_run: bool
) -> None:
    target = target_root / relative_path
    if target.exists():
        result.skipped.append(f"{relative_path} already exists")
        return

    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    result.created.append(relative_path)


def ensure_agents_block(target_root: Path, result: Result, dry_run: bool) -> None:
    relative_path = "AGENTS.md"
    target = target_root / relative_path
    block = read_asset("AGENTS_MEMORY_BANK_BLOCK.md").rstrip() + "\n"

    if not target.exists():
        if not dry_run:
            target.write_text(block, encoding="utf-8")
        result.created.append(relative_path)
        return

    existing = target.read_text(encoding="utf-8")
    has_begin = BEGIN_MARKER in existing
    has_end = END_MARKER in existing

    if has_begin and has_end:
        result.skipped.append("AGENTS.md already contains Project Memory Bank block")
        return

    if has_begin or has_end:
        result.warnings.append(
            "AGENTS.md contains a partial Project Memory Bank marker block; left unchanged"
        )
        return

    if existing.endswith("\n\n"):
        separator = ""
    else:
        separator = "\n\n"

    if not dry_run:
        target.write_text(existing + separator + block, encoding="utf-8")
    result.created.append("AGENTS.md Project Memory Bank block")


def initialize(target_root: Path, dry_run: bool = False) -> Result:
    target_root = target_root.resolve()
    result = Result(created=[], skipped=[], warnings=[])

    if not target_root.exists():
        if dry_run:
            result.created.append(str(target_root))
        else:
            target_root.mkdir(parents=True, exist_ok=True)

    templates = [
        "projectbrief.md",
        "productContext.md",
        "activeContext.md",
        "systemPatterns.md",
        "techContext.md",
        "progress.md",
    ]
    for name in templates:
        write_if_missing(
            target_root,
            f"memory-bank/{name}",
            read_asset(f"memory-bank/{name}"),
            result,
            dry_run,
        )

    ensure_agents_block(target_root, result, dry_run)
    return result


def print_result(target_root: Path, result: Result, dry_run: bool) -> None:
    mode = "Dry run" if dry_run else "Initialized"
    print(f"{mode}: {target_root.resolve()}")

    if result.created:
        print("\nCreated:")
        for item in result.created:
            print(f"  - {item}")

    if result.skipped:
        print("\nSkipped:")
        for item in result.skipped:
            print(f"  - {item}")

    if result.warnings:
        print("\nWarnings:")
        for item in result.warnings:
            print(f"  - {item}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize or repair a project-local Memory Bank."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target project directory. Defaults to the current directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without writing files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_root = Path(args.target)
    result = initialize(target_root, dry_run=args.dry_run)
    print_result(target_root, result, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
