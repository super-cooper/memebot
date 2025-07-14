#!/usr/bin/env python3

"""
A script to verify Python version consistency across different project configuration files.

This script ensures that Python versions specified in different project files
(Dockerfile, pyproject.toml, and GitHub workflow files) are consistent with each other.
It extracts the Python version from the Dockerfile as the source of truth and compares
it with versions specified in other configuration files.

The script checks:
- Python version in Dockerfile (source of truth)
- Python version in pyproject.toml (mypy configuration)
- Python versions in GitHub workflow files (comma separated list of paths)

Usage:
    python verify_python_versions.py <dockerfile_path> <pyproject_path> <workflow_paths_csv>

Returns:
    Exit code 0 if all versions are consistent
    Exit code 1 if any inconsistencies are found or errors occur
"""
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, cast


def extract_version_from_dockerfile(dockerfile_path: Path) -> tuple[str, str]:
    """Extract the Python version from the Dockerfile (source of truth).

    Finds all instances of 'FROM python:*', verifies they're all the same,
    and returns the common version.
    """
    if not dockerfile_path.exists():
        print(f"Error: {dockerfile_path} not found")
        sys.exit(1)

    dockerfile_content = dockerfile_path.read_text()

    # Find all Python image references in the Dockerfile
    python_images = re.findall(r"^FROM python:(\d+)\.?(\d+)?.*", dockerfile_content)

    if not python_images:
        print(f"Error: No Python images found in {dockerfile_path}")
        sys.exit(1)

    base_version = cast(tuple[str, str | None], python_images[0])
    if base_version[1] is None:
        print("Dockerfile python does not specify minor version.")
        sys.exit(1)

    if not all(version == base_version for version in python_images):
        print(
            f"Error: Inconsistent Python images in {dockerfile_path}: {python_images}"
        )
        sys.exit(1)

    return cast(tuple[str, str], base_version)


@dataclass(frozen=True)
class VersionCheckResult:
    success: bool
    message: str | None


def check_for_version_in_file(
    path: Path,
    extract_versions: Callable[[str], list[tuple[str, str]]],
    source_version: tuple[str, str],
) -> VersionCheckResult:
    """
    Checks if a given file declares the correct python versions.

    Accepts a path and a lambda which defines how to extract versions from that path,
    as well as a source version to compare against
    """
    if not path.exists():
        return VersionCheckResult(success=False, message=f"{path.name} not found.")

    python_versions = extract_versions(path.read_text())
    if not python_versions:
        return VersionCheckResult(
            success=False, message=f"{path.name} has no python versions."
        )

    errors = [
        f"{path.name} has mismatched version: {python_version}"
        for python_version in python_versions
        if source_version != python_version
    ]

    return VersionCheckResult(
        success=len(errors) == 0, message="\n".join(errors) if errors else None
    )


def main(dockerfile_path: str, pyproject_path: str, workflow_paths_csv: str) -> None:
    source_version = extract_version_from_dockerfile(Path(dockerfile_path.strip()))
    print(f"Source of truth Python version: {source_version}")

    results = [
        check_for_version_in_file(
            Path(pyproject_path.strip()),
            lambda content: re.findall(
                r'python_version\s*=\s*"(\d+)\.?(\d+)?.*"', content
            ),
            source_version,
        ),
        *(
            check_for_version_in_file(
                Path(workflow_path.strip()),
                lambda content: re.findall(
                    r"python-version:\s*(\d+)\.?(\d+)?.*", content
                ),
                source_version,
            )
            for workflow_path in workflow_paths_csv.split(",")
        ),
    ]

    print("\n".join(result.message for result in results if result.message is not None))

    if not all(result.success for result in results):
        sys.exit(1)
    else:
        print("All Python version references are consistent!")


if __name__ == "__main__":
    main(*sys.argv[1:])
