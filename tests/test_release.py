"""Verify the distributable, version gates and exclusion of local files."""

from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
from zipfile import ZipFile

import pytest

from script.build_release import PREFIX, build_release, release_version

ROOT = Path(__file__).parents[1]


@pytest.fixture
def release_tree(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    for name in ("package.json", "package-lock.json", "LICENSE"):
        shutil.copy2(ROOT / name, root / name)
    for name in (PREFIX, "frontend/public", "docs/releases"):
        shutil.copytree(
            ROOT / name,
            root / name,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "add", PREFIX], cwd=root, check=True)
    return root


def test_zip_is_complete_extractable_reproducible_and_has_only_runtime(
    release_tree, tmp_path
):
    runtime = release_tree / PREFIX
    (runtime / "untracked-private.json").write_text('{"example": "not-for-release"}')
    cache = runtime / "__pycache__"
    cache.mkdir()
    (cache / "local.pyc").write_bytes(b"local-cache")
    one = build_release(release_tree, tmp_path / "one", "v0.1.0")
    two = build_release(release_tree, tmp_path / "two", "v0.1.0")
    assert one.read_bytes() == two.read_bytes()
    assert (one.parent / "SHA256SUMS").read_text() == (
        f"{sha256(one.read_bytes()).hexdigest()}  plantbased.zip\n"
    )
    with ZipFile(one) as archive:
        assert archive.testzip() is None
        assert all(name.startswith("plantbased/") for name in archive.namelist())
        assert not any(".." in Path(name).parts for name in archive.namelist())
        assert not any(
            "private" in name or "__pycache__" in name for name in archive.namelist()
        )
        assert archive.read("plantbased/LICENSE") == (ROOT / "LICENSE").read_bytes()
        assert (
            json.loads(archive.read("plantbased/manifest.json"))["version"] == "0.1.0"
        )
        tracked = subprocess.check_output(
            ["git", "ls-files", "-z", "--", PREFIX], cwd=release_tree
        ).decode()
        assert len(archive.namelist()) == len(tracked.strip("\0").split("\0")) + 1
        for name in tracked.strip("\0").split("\0"):
            inside = Path(name).relative_to("custom_components").as_posix()
            assert archive.read(inside) == (release_tree / name).read_bytes()
        archive.extractall(tmp_path / "install/custom_components")
    installed = tmp_path / "install/custom_components/plantbased"
    assert (installed / "frontend/plantbased.js").is_file()
    assert len(list((installed / "frontend/illustrations").glob("*.svg"))) == 12
    for path in installed.glob("*.py"):
        compile(path.read_text(), str(path), "exec")


@pytest.mark.parametrize("tag", ["v0.2.0", "0.1.0", "v0.1.0-rc.1", "v0.1.0;invalid"])
def test_wrong_or_unstable_tag_is_rejected_before_output(release_tree, tmp_path, tag):
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="tag"):
        build_release(release_tree, output, tag)
    assert not output.exists()


@pytest.mark.parametrize("name", ["package.json", "package-lock.json"])
def test_frontend_version_mismatch_is_rejected(release_tree, name):
    path = release_tree / name
    data = json.loads(path.read_text())
    data["version"] = "0.2.0"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="versions differ"):
        release_version(release_tree, "v0.1.0")


def test_lock_root_version_must_match(release_tree):
    path = release_tree / "package-lock.json"
    data = json.loads(path.read_text())
    data["packages"][""]["version"] = "0.2.0"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="versions differ"):
        release_version(release_tree, None)


@pytest.mark.parametrize(
    "name",
    [
        "frontend/plantbased.js",
        "translations/de.json",
        "frontend/THIRD_PARTY_LICENSES.md",
    ],
)
def test_missing_runtime_file_is_rejected(release_tree, tmp_path, name):
    (release_tree / PREFIX / name).unlink()
    with pytest.raises(ValueError, match="integration file"):
        build_release(release_tree, tmp_path / "output")


def test_missing_release_notes_are_rejected(release_tree):
    (release_tree / "docs/releases/v0.1.0.md").unlink()
    with pytest.raises(ValueError, match="release notes"):
        release_version(release_tree, "v0.1.0")


def test_changed_or_missing_illustration_is_rejected(release_tree, tmp_path):
    (release_tree / PREFIX / "frontend/illustrations/monstera.svg").write_text("<svg/>")
    with pytest.raises(ValueError, match="twelve original SVGs"):
        build_release(release_tree, tmp_path / "output")


@pytest.mark.parametrize("unsafe", ["linked.json", "__pycache__/cached.pyc"])
def test_tracked_links_and_caches_are_rejected(release_tree, tmp_path, unsafe):
    path = release_tree / PREFIX / unsafe
    path.parent.mkdir(exist_ok=True)
    if unsafe == "linked.json":
        path.symlink_to(release_tree / "package.json")
    else:
        path.write_bytes(b"cache")
    subprocess.run(["git", "add", PREFIX], cwd=release_tree, check=True)
    with pytest.raises(ValueError, match="Unexpected integration file"):
        build_release(release_tree, tmp_path / "output")
