"""Check this project and build a reproducible, skill-only release (stdlib only)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "lecture-tutor"
SKIP = {".git", ".local", "dist", ".venv", "__pycache__"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check() -> tuple[str, list[Path]]:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    require(bool(re.fullmatch(r"\d+\.\d+\.\d+", version)), "Invalid VERSION")
    entrypoint = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    front = re.match(r"\A---\n(.*?)\n---(?:\n|$)", entrypoint, re.DOTALL)
    require(front is not None, "SKILL.md needs YAML front matter")
    fields = dict(re.findall(r"^([a-z_-]+):\s*(.+)$", front.group(1), re.MULTILINE))
    require(fields.get("name") == SKILL.name, "Skill name does not match directory")
    require(bool(fields.get("description", "").strip(' \"\'')), "Missing description")

    files = sorted((path for path in SKILL.rglob("*") if path.is_file()),
                   key=lambda path: path.relative_to(SKILL).as_posix())
    require(bool(files), "Skill has no files")
    for path in SKILL.rglob("*"):
        require(not path.is_symlink(), f"Symlink is not a release input: {path.name}")
        require(not any(part in SKIP for part in path.relative_to(SKILL).parts),
                f"Unexpected cache or local state in skill: {path.name}")

    metadata = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
    short = re.search(r'^  short_description:\s*(".*")\s*$', metadata, re.MULTILINE)
    require(short is not None, "Missing UI short description")
    require(25 <= len(json.loads(short.group(1))) <= 64, "UI description needs 25–64 characters")

    checked_links = 0
    for path in ROOT.rglob("*.md"):
        if any(part in SKIP for part in path.relative_to(ROOT).parts):
            continue
        content = path.read_text(encoding="utf-8")
        require("\ufffd" not in content, f"Invalid text encoding: {path.name}")
        targets = re.findall(r"\]\(([^)\n]+)\)", content)
        targets += re.findall(r'(?:href|src)="([^"]+)"', content)
        for raw in targets:
            target = raw.strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("#"):
                continue
            destination = (path.parent / unquote(parsed.path)).resolve()
            require(destination.is_relative_to(ROOT), f"Nonportable link in {path.name}: {target}")
            require(destination.exists(), f"Broken link in {path.name}: {target}")
            checked_links += 1
    ET.parse(ROOT / "docs" / "assets" / "cover.svg")

    requests = json.loads((ROOT / "validation" / "requests.json").read_text(encoding="utf-8"))
    require(len({item["id"] for item in requests}) == len(requests), "Duplicate request IDs")
    for item in requests:
        for attachment in item["attachments"]:
            require((ROOT / "validation" / attachment).is_file(), f"Missing fixture: {attachment}")
        require((ROOT / "validation" / "trial-001" / f'{item["id"]}.md').is_file(),
                f'Missing trial output: {item["id"]}')

    baseline = json.loads((ROOT / "validation" / "structure-results.json").read_text(encoding="utf-8"))
    manifest = {name.replace("\\", "/"): digest for name, digest in baseline["skill_sha256"].items()}
    actual = {path.relative_to(SKILL).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in files}
    require(actual == manifest, "Skill content differs from the behavior-validated snapshot; revalidate and update its record")
    print(f"CHECK PASSED: {len(files)} skill files, {checked_links} local links, {len(requests)} trial records")
    return version, files


def build(version: str, files: list[Path]) -> Path:
    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    archive_path = output / f"lecture-tutor-v{version}.zip"
    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            info = ZipInfo(path.relative_to(ROOT).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    with ZipFile(archive_path) as archive:
        require(archive.testzip() is None, "Release archive is corrupt")
        expected_names = {path.relative_to(ROOT).as_posix() for path in files}
        require(set(archive.namelist()) == expected_names, "Unexpected release contents")
        for path in files:
            require(archive.read(path.relative_to(ROOT).as_posix()) == path.read_bytes(),
                    f"Archive content mismatch: {path.name}")
    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    (output / "SHA256SUMS.txt").write_text(f"{digest}  {archive_path.name}\n", encoding="utf-8")
    print(f"BUILT: {archive_path.relative_to(ROOT).as_posix()} ({len(files)} files)")
    print(f"SHA256: {digest}")
    return archive_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check inputs without building an archive")
    args = parser.parse_args()
    try:
        version, files = check()
        if not args.check:
            build(version, files)
    except (OSError, ValueError, KeyError, ET.ParseError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
