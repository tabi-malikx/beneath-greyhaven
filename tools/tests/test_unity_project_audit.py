import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from unity_project_audit import audit_project, main


class UnityProjectAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "Project"
        for folder in ("Assets", "Packages", "ProjectSettings"):
            (self.root / folder).mkdir(parents=True)
        (self.root / "Packages/manifest.json").write_text('{"dependencies": {}}')
        (self.root / "ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 6000.0.1f1\n")

    def asset(self, name, guid="0123456789abcdef0123456789abcdef"):
        path = self.root / "Assets" / name
        path.write_text("sample")
        path.with_name(path.name + ".meta").write_text("fileFormatVersion: 2\nguid: " + guid + "\n")
        return path

    def codes(self):
        return {f.code for f in audit_project(self.root).findings}

    def test_valid_project_and_editor_version(self):
        self.asset("Door.cs")
        result = audit_project(self.root)
        self.assertTrue(result.ok)
        self.assertEqual("6000.0.1f1", result.editor_version)

    def test_missing_project_directories(self):
        (self.root / "Assets").rmdir()
        self.assertIn("MISSING_DIRECTORY", self.codes())
        self.assertEqual("MISSING_PROJECT", audit_project(self.root / "absent").findings[0].code)

    def test_file_and_directory_metadata_are_required(self):
        (self.root / "Assets/Door.cs").write_text("sample")
        (self.root / "Assets/Scenes").mkdir()
        result = audit_project(self.root)
        self.assertEqual({"Assets/Door.cs", "Assets/Scenes"}, {f.path for f in result.findings})
        self.assertEqual({"MISSING_META"}, self.codes())

    def test_duplicate_guids_are_case_insensitive(self):
        self.asset("Door.cs", "a" * 32)
        self.asset("Window.cs", "A" * 32)
        result = audit_project(self.root)
        duplicate = [f for f in result.findings if f.code == "DUPLICATE_GUID"]
        self.assertEqual(1, len(duplicate))
        self.assertIn("Assets/Door.cs.meta", duplicate[0].message)

    def test_orphan_and_invalid_metadata(self):
        path = self.asset("Door.cs")
        path.unlink()
        self.assertIn("ORPHAN_META", self.codes())
        path.write_text("sample")
        path.with_name(path.name + ".meta").write_text("guid: not-a-guid\n")
        self.assertIn("INVALID_GUID", self.codes())

    def test_invalid_and_missing_manifests(self):
        manifest = self.root / "Packages/manifest.json"
        for invalid in ("{", "[]", '{"dependencies": []}', '{"dependencies": {"x": 4}}'):
            with self.subTest(manifest=invalid):
                manifest.write_text(invalid)
                self.assertIn("INVALID_MANIFEST", self.codes())
        manifest.unlink()
        self.assertIn("MISSING_MANIFEST", self.codes())

    def test_version_file_validation(self):
        version = self.root / "ProjectSettings/ProjectVersion.txt"
        for invalid in ("unexpected content\n", "m_EditorVersion:\nm_EditorVersionWithRevision: 6000.0.1f1\n"):
            with self.subTest(version=invalid):
                version.write_text(invalid)
                self.assertIn("INVALID_VERSION", self.codes())
        version.unlink()
        self.assertIn("MISSING_VERSION", self.codes())

    def test_hidden_and_backup_paths_are_ignored(self):
        (self.root / "Assets/.cache").mkdir()
        (self.root / "Assets/.cache/file").write_text("ignored")
        (self.root / "Assets/Archive~").mkdir()
        (self.root / "Assets/Archive~/file").write_text("ignored")
        (self.root / "Assets/.DS_Store").write_text("ignored")
        self.assertTrue(audit_project(self.root).ok)

    def test_symlinks_are_not_followed(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (outside / "private.txt").write_text("do not read")
        link = self.root / "Assets/External"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symbolic links are not available.")
        result = audit_project(self.root)
        self.assertEqual(["Assets/External"], [f.path for f in result.findings])
        self.assertEqual("SYMLINK", result.findings[0].code)

    def test_unreadable_utf8_metadata_is_reported(self):
        path = self.asset("Door.cs")
        path.with_name(path.name + ".meta").write_bytes(b"\xff\xfe\xff")
        self.assertIn("UNREADABLE_FILE", self.codes())

    def test_cli_json_and_exit_status(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main([str(self.root), "--json"])
        self.assertEqual(0, code)
        self.assertTrue(json.loads(output.getvalue())["ok"])
        (self.root / "Assets/MissingMeta.cs").write_text("sample")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(1, main([str(self.root)]))

    def test_audit_never_modifies_project_files(self):
        self.asset("Door.cs")
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        audit_project(self.root)
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
