"""Build a deterministic manual-install ZIP from tracked integration files."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "plantbased"
PREFIX = f"custom_components/{DOMAIN}/"
STABLE_VERSION = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")


def release_version(root: Path, tag: str | None) -> str:
    """Require one stable version across the tag and all version manifests."""
    manifest = json.loads((root / PREFIX / "manifest.json").read_text())
    version = manifest["version"]
    if not isinstance(version, str) or not STABLE_VERSION.fullmatch(version):
        raise ValueError("Release version must be stable MAJOR.MINOR.PATCH")
    if tag is not None and tag != f"v{version}":
        raise ValueError("Release tag does not match manifest version")
    package = json.loads((root / "package.json").read_text())
    lock = json.loads((root / "package-lock.json").read_text())
    if any(
        value != version
        for value in (
            package["version"],
            lock["version"],
            lock["packages"][""]["version"],
        )
    ):
        raise ValueError("Frontend and integration versions differ")
    if manifest["domain"] != DOMAIN or manifest["requirements"]:
        raise ValueError("Expected PlantBased with no runtime Python requirements")
    notes = root / "docs/releases" / f"v{version}.md"
    if not notes.is_file() or not notes.read_text().strip():
        raise ValueError("Version-specific release notes are missing")
    return version


def build_release(root: Path, output: Path, tag: str | None = None) -> Path:
    """Package only tracked runtime files and the repository license."""
    release_version(root, tag)
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z", "--", PREFIX], cwd=root
    ).decode()
    paths = sorted(Path(name) for name in tracked.split("\0") if name)
    files: dict[str, bytes] = {}
    for relative in paths:
        path = root / relative
        inside = relative.relative_to(PREFIX)
        if (
            path.is_symlink()
            or not path.is_file()
            or any(
                part.startswith(".") or part == "__pycache__" for part in inside.parts
            )
            or inside.suffix
            not in {".py", ".json", ".yaml", ".js", ".svg", ".png", ".md"}
        ):
            raise ValueError(f"Unexpected integration file: {relative}")
        files[f"{DOMAIN}/{inside.as_posix()}"] = path.read_bytes()
    required = {
        f"{DOMAIN}/__init__.py",
        f"{DOMAIN}/manifest.json",
        f"{DOMAIN}/strings.json",
        f"{DOMAIN}/services.yaml",
        f"{DOMAIN}/translations/en.json",
        f"{DOMAIN}/translations/de.json",
        f"{DOMAIN}/frontend/plantbased.js",
        f"{DOMAIN}/frontend/THIRD_PARTY_LICENSES.md",
        f"{DOMAIN}/brand/icon.png",
    }
    if not required.issubset(files):
        raise ValueError(f"Missing runtime files: {sorted(required - files.keys())}")
    presets = sorted((root / "frontend/public/illustrations").glob("*.svg"))
    if len(presets) != 12 or any(
        files.get(f"{DOMAIN}/frontend/illustrations/{path.name}") != path.read_bytes()
        for path in presets
    ):
        raise ValueError("All twelve original SVGs must match the shipped files")
    files[f"{DOMAIN}/LICENSE"] = (root / "LICENSE").read_bytes()
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"{DOMAIN}.zip"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=9) as zipped:
        for name, content in sorted(files.items()):
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            zipped.writestr(info, content, compress_type=ZIP_DEFLATED, compresslevel=9)
    with ZipFile(archive) as zipped:
        if zipped.testzip() is not None:
            raise ValueError("Release ZIP integrity check failed")
    checksum = sha256(archive.read_bytes()).hexdigest()
    (output / "SHA256SUMS").write_text(f"{checksum}  {archive.name}\n")
    return archive


def main() -> None:
    """Run without Home Assistant or third-party Python dependencies."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", help="Expected stable tag, e.g. v0.1.0")
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    try:
        archive = build_release(ROOT, args.output, args.tag)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Release packaging failed: {error}\n")
    print(f"Verified {archive.name}: {archive.stat().st_size} bytes")
    print((archive.parent / "SHA256SUMS").read_text().strip())


if __name__ == "__main__":
    main()
