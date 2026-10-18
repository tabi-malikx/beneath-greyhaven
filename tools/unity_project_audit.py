#!/usr/bin/env python3
"""Read-only structural and asset-metadata checks for a Unity project."""

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class Finding:
    code: str
    path: str
    message: str


@dataclass
class AuditResult:
    editor_version: Optional[str]
    findings: List[Finding]

    @property
    def ok(self) -> bool:
        return not self.findings


def audit_project(project_root: Path) -> AuditResult:
    """Check project structure and Assets metadata without modifying files."""
    root = Path(project_root).resolve()
    findings: List[Finding] = []

    def report(code: str, path: Path, message: str) -> None:
        findings.append(Finding(code, path.relative_to(root).as_posix(), message))

    def read(path: Path) -> Optional[str]:
        try:
            return path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError):
            report("UNREADABLE_FILE", path, "Cannot read this file as UTF-8 text.")
            return None

    if not root.is_dir():
        return AuditResult(None, [Finding("MISSING_PROJECT", ".", "Project directory does not exist.")])

    required = [root / "Assets", root / "Packages", root / "ProjectSettings"]
    for directory in required:
        if directory.is_symlink():
            report("SYMLINK", directory, "Project folders must be real directories for this audit.")
        elif not directory.is_dir():
            report("MISSING_DIRECTORY", directory, "Required Unity project directory is missing.")
    if findings:
        return AuditResult(None, findings)

    manifest = root / "Packages/manifest.json"
    if manifest.is_symlink():
        report("SYMLINK", manifest, "Symbolic links are not followed.")
    elif not manifest.is_file():
        report("MISSING_MANIFEST", manifest, "Unity package manifest is missing.")
    else:
        text = read(manifest)
        if text is not None:
            try:
                data = json.loads(text)
                dependencies = data.get("dependencies") if isinstance(data, dict) else None
                if not isinstance(dependencies, dict) or not all(
                    isinstance(k, str) and isinstance(v, str) for k, v in dependencies.items()
                ):
                    report("INVALID_MANIFEST", manifest, "Expected a JSON object with a dependencies mapping of strings.")
            except json.JSONDecodeError:
                report("INVALID_MANIFEST", manifest, "Package manifest is not valid JSON.")

    version_file = root / "ProjectSettings/ProjectVersion.txt"
    version = None
    if version_file.is_symlink():
        report("SYMLINK", version_file, "Symbolic links are not followed.")
    elif not version_file.is_file():
        report("MISSING_VERSION", version_file, "Unity editor version file is missing.")
    else:
        text = read(version_file)
        if text is not None:
            match = re.search(r"^m_EditorVersion:[ \t]*(\S+)[ \t]*$", text, re.MULTILINE)
            if match:
                version = match.group(1)
            else:
                report("INVALID_VERSION", version_file, "No m_EditorVersion entry was found.")

    guids = {}

    def walk_error(error: OSError) -> None:
        path = Path(error.filename) if error.filename else root / "Assets"
        report("UNREADABLE_DIRECTORY", path, "Cannot list this asset directory.")

    for parent, directories, files in os.walk(root / "Assets", followlinks=False, onerror=walk_error):
        # Unity ignores hidden paths and names ending in a tilde.
        directories[:] = sorted(d for d in directories if not d.startswith(".") and not d.endswith("~"))
        names = sorted(directories + [f for f in files if not f.startswith(".") and not f.endswith("~")])
        for name in names:
            path = Path(parent) / name
            if path.is_symlink():
                report("SYMLINK", path, "Symbolic links are not followed.")
                continue
            if path.suffix == ".meta" and path.is_file():
                asset = path.with_name(path.name[:-5])
                if not asset.exists():
                    report("ORPHAN_META", path, "The matching asset or directory is missing.")
                text = read(path)
                if text is None:
                    continue
                match = re.search(r"^guid:[ \t]*([0-9a-fA-F]{32})[ \t]*$", text, re.MULTILINE)
                if not match:
                    report("INVALID_GUID", path, "Expected a 32-digit hexadecimal asset GUID.")
                    continue
                guid = match.group(1).lower()
                if guid in guids:
                    report("DUPLICATE_GUID", path, "GUID also appears in " + guids[guid] + ".")
                else:
                    guids[guid] = path.relative_to(root).as_posix()
            else:
                meta = path.with_name(path.name + ".meta")
                if not meta.is_file() or meta.is_symlink():
                    report("MISSING_META", path, "Matching .meta file is missing or is a symbolic link.")

    return AuditResult(version, sorted(findings, key=lambda f: (f.path, f.code)))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--json", action="store_true", help="Emit machine-readable results.")
    args = parser.parse_args(argv)
    result = audit_project(args.project)
    if args.json:
        print(json.dumps({"ok": result.ok, **asdict(result)}, indent=2))
    else:
        print("Unity project audit: " + ("PASS" if result.ok else "FAIL"))
        if result.editor_version:
            print("Editor version: " + result.editor_version)
        for finding in result.findings:
            print(f"{finding.code}: {finding.path}: {finding.message}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
