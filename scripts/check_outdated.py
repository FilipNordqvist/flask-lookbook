#!/usr/bin/env python3
"""
Check for outdated packages in requirements.txt.

This script compares the versions in requirements.txt with the latest
available versions on PyPI.
"""

import subprocess
import sys
from pathlib import Path


def get_latest_version(package_name: str) -> str | None:
    """Get the latest version of a package from PyPI."""
    try:
        result = subprocess.run(
            ["pip", "index", "versions", package_name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            # Parse output to find LATEST version
            for line in result.stdout.split("\n"):
                if "LATEST:" in line:
                    latest = line.split("LATEST:")[1].strip()
                    return latest
    except Exception:
        pass
    return None


def parse_requirements(file_path: Path) -> list[tuple[str, str]]:
    """Parse requirements.txt and return list of (package, version) tuples."""
    requirements = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            # Remove inline comments
            if "#" in line:
                line = line.split("#")[0].strip()
            # Parse package==version
            if "==" in line:
                parts = line.split("==")
                if len(parts) == 2:
                    package = parts[0].strip()
                    version = parts[1].strip()
                    requirements.append((package, version))
    return requirements


def main():
    """Main function to check for outdated packages."""
    project_root = Path(__file__).parent.parent
    requirements_file = project_root / "requirements.txt"

    if not requirements_file.exists():
        print(f"Error: {requirements_file} not found", file=sys.stderr)
        sys.exit(1)

    requirements = parse_requirements(requirements_file)
    outdated = []

    print("Checking for outdated packages...")
    print("=" * 60)

    for package, current_version in requirements:
        latest_version = get_latest_version(package)
        if latest_version and latest_version != current_version:
            outdated.append((package, current_version, latest_version))
            print(f"⚠️  {package:30} {current_version:15} → {latest_version}")

    if not outdated:
        print("✅ All packages are up to date!")
    else:
        print(f"\nFound {len(outdated)} outdated package(s)")
        print("\nTo update, you can run:")
        print(
            "  mise x -- pip install --upgrade "
            + " ".join([pkg for pkg, _, _ in outdated])
        )

    return 0 if not outdated else 1


if __name__ == "__main__":
    sys.exit(main())
