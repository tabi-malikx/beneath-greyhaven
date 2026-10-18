# Adding the Unity project

This repository contains showcase documentation and read-only tooling. The full Unity game project has not been uploaded.

When the source is ready to share, place the Unity project at the repository root, retaining `Assets/`, `Packages/` and `ProjectSettings/`. Keep asset `.meta` files with their assets. The root `.gitignore` excludes Unity caches, generated files and build output.

Record the actual Unity editor version, package dependencies, entry scene and build target in the main README after import. Add instructions only after verifying them against the real source project.

Before importing, run the [Unity project audit](../tools/README.md) on the actual project's root directory. Fix missing or duplicated asset metadata using the original Unity project, then run the audit again. The audit reports findings without changing your files.

The `media/` directory is for genuine project screenshots and short gameplay captures. Client-owned source and assets should only be published when their distribution is authorized.
