#!/usr/bin/env python3
"""Build standalone binaries for Simple Video Slicer with PyInstaller."""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Tuple

ROOT = Path(__file__).resolve().parent.parent
SRC_MAIN = ROOT / "src" / "video_slicer" / "main.py"

SUPPORTED_PLATFORMS: Dict[str, Tuple[str, str]] = {
    "linux_86_64": ("linux", "x86_64"),
    "linux_arm": ("linux", "arm64"),
    "windows_86_64": ("windows", "x86_64"),
    "windows_arm": ("windows", "arm64"),
    "macos_86_64": ("darwin", "x86_64"),
    "macos_arm": ("darwin", "arm64"),
}


def _normalize_arch(machine: str) -> str:
    machine = machine.lower()
    if machine in {"amd64", "x86_64", "x64"}:
        return "x86_64"
    if machine in {"aarch64", "arm64"}:
        return "arm64"
    if machine.startswith("arm"):
        return "arm"
    return machine


def _load_version() -> str:
    sys.path.insert(0, str(ROOT / "src"))
    try:
        import video_slicer  # type: ignore
    finally:
        sys.path.pop(0)
    version = getattr(video_slicer, "__version__", "0.0.0")
    return version


def _format_version(version: str) -> str:
    major, *rest = version.split(".")
    minor = rest[0] if rest else "0"
    return f"{major}_{minor}"


def build_binary(target: str, *, clean: bool = False, force: bool = False) -> None:
    if target not in SUPPORTED_PLATFORMS:
        raise SystemExit(f"Unsupported target '{target}'. Available: {', '.join(SUPPORTED_PLATFORMS)}")

    required_os, required_arch = SUPPORTED_PLATFORMS[target]

    host_os = platform.system().lower()
    host_arch = _normalize_arch(platform.machine())

    if not force:
        if host_os != required_os:
            raise SystemExit(
                "\n".join(
                    [
                        f"Current host '{host_os}/{host_arch}' cannot natively produce '{target}' binaries.",
                        "Please run the build on the matching operating system or use --force at your own risk.",
                    ]
                )
            )
        if required_arch != host_arch:
            raise SystemExit(
                "\n".join(
                    [
                        f"Target '{target}' expects architecture '{required_arch}', but this host reports '{host_arch}'.",
                        "Use the matching hardware platform or pass --force to try anyway.",
                    ]
                )
            )

    if shutil.which("pyinstaller") is None:
        raise SystemExit("PyInstaller is not available in PATH. Install it with 'uv pip install pyinstaller' or 'pip install pyinstaller'.")

    if not SRC_MAIN.exists():
        raise SystemExit(f"Entry point {SRC_MAIN} does not exist. Run the script from the project root.")

    version = _load_version()
    version_tag = _format_version(version)
    binary_name = f"svs_{version_tag}_{target}"

    dist_dir = ROOT / "dist"
    work_dir = ROOT / "build" / binary_name
    spec_dir = ROOT / "build" / "spec"

    dist_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    spec_dir.mkdir(parents=True, exist_ok=True)

    if clean:
        shutil.rmtree(work_dir, ignore_errors=True)
        possible_binary = dist_dir / binary_name
        if possible_binary.exists():
            if possible_binary.is_dir():
                shutil.rmtree(possible_binary, ignore_errors=True)
            else:
                possible_binary.unlink()

    env = os.environ.copy()
    env.setdefault("PYINSTALLER_CONFIG_DIR", str(ROOT / ".pyinstaller"))

    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name",
        binary_name,
        "--distpath",
        str(dist_dir),
        "--workpath",
        str(work_dir),
        "--specpath",
        str(spec_dir),
        "--collect-all",
        "video_slicer",
        str(SRC_MAIN),
    ]

    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, env=env)
    print(f"\nBinary available at {dist_dir / binary_name}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build platform-specific binaries for Simple Video Slicer.")
    parser.add_argument("target", choices=tuple(SUPPORTED_PLATFORMS.keys()), help="Build target identifier, e.g. linux_86_64")
    parser.add_argument("--clean", action="store_true", help="Remove previous build artifacts before building")
    parser.add_argument("--force", action="store_true", help="Skip host platform check (may fail on cross-compilation)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    build_binary(args.target, clean=args.clean, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
