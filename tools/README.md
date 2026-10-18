# Unity project audit

A read-only Python tool for checking a Unity project before source import. It uses Python 3.9+ and the standard library; Unity and third-party Python packages are not required to run the audit.

## Run

From this repository's root:

```sh
python3 tools/unity_project_audit.py /path/to/your/UnityProject
python3 tools/unity_project_audit.py /path/to/your/UnityProject --json
```

On Windows, `py -3` can be used instead of `python3`.

Use the directory containing `Assets`, `Packages` and `ProjectSettings`. The showcase repository itself is not a complete Unity project.

## Checks

- Required project directories, a valid package manifest, and an editor version entry.
- Missing `.meta` files for asset files and directories.
- Orphaned `.meta` files, invalid GUIDs, and duplicate GUIDs.
- Unreadable text files and symbolic links, which are not followed.

Hidden paths and names ending in `~` are excluded. The tool prints relative asset paths and never writes to the audited project.

Exit code `0` means these checks passed; `1` means findings were reported. Passing this audit does not validate package availability, scene references, script compilation, licensing, build success, or whether files are safe to publish.

## Tests

```sh
python3 -m unittest discover -s tools/tests -v
```

Tests use temporary project fixtures and cover metadata errors, project structure, CLI output, symlink handling and unchanged input files.

## Reference

Unity's [asset metadata documentation](https://docs.unity3d.com/6000.0/Documentation/Manual/AssetMetadata.html) explains how `.meta` files preserve asset identity and references.
