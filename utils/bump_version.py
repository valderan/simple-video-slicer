#!/usr/bin/env python3
"""Update the project version across tracked metadata files."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INIT_FILE = ROOT / "src" / "video_slicer" / "__init__.py"
VERSION_PATTERN = re.compile(r"__version__\s*=\s*\"(?P<version>[^\"]+)\"")


def read_current_version() -> str:
    content = INIT_FILE.read_text(encoding="utf-8")
    match = VERSION_PATTERN.search(content)
    if not match:
        raise RuntimeError(f"Cannot find __version__ declaration in {INIT_FILE}")
    return match.group("version")


def write_new_version(new_version: str) -> None:
    content = INIT_FILE.read_text(encoding="utf-8")
    updated = VERSION_PATTERN.sub(f'__version__ = "{new_version}"', content)
    INIT_FILE.write_text(updated, encoding="utf-8")


def validate_version(value: str) -> str:
    if not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise argparse.ArgumentTypeError("Version must follow semantic versioning: MAJOR.MINOR.PATCH")
    return value


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bump the Simple Video Slicer version.")
    parser.add_argument("new_version", type=validate_version, help="New semantic version, e.g. 0.2.0")
    parser.add_argument("--dry-run", action="store_true", help="Show the planned change without editing files")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    current_version = read_current_version()

    if args.dry_run:
        print(f"Current version: {current_version}\nProposed version: {args.new_version}")
        return 0

    if args.new_version == current_version:
        print(f"Version {args.new_version} is already set; no changes made.")
        return 0

    write_new_version(args.new_version)
    print(f"Updated version: {current_version} -> {args.new_version}")
    print("Remember to update CHANGELOG.md and tag the release.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
