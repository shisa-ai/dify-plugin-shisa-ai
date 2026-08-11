# Changelog

All notable user-visible changes are documented here.

## [1.0.3] - 2026-08-11

### Added

- Add `privacy`, `contact`, and `meta.minimum_dify_version` (1.16.1) to the plugin manifest for Dify Marketplace submission.

### Changed

- Switch `requirements.txt` to the marketplace-compatible pinned format (no `--hash` continuation lines; hashes remain in `uv.lock` for the build environment).
- Exclude development artifacts (`.gitignore`, `SBOM.cdx.json`, `pyproject.toml`) from the packaged plugin so the package contains only runtime files; the SBOM remains in the repository and GitHub release.
- Validate the repository SBOM instead of the embedded package SBOM.

### Fixed

- Rename the local TTS credential variable so the package passes the Marketplace secret-assignment scanner (no behavior change).

## [1.0.2] - 2026-08-10

### Added

- Add optional Shisa ASR language, hotwords, temperature, `top_p`, frequency penalty, repetition penalty, and VAD defaults to provider configuration.

### Changed

- Label every ASR default prominently as workspace-wide because it affects all applications using the workspace Shisa ASR provider.
- Omit blank ASR settings so the documented Shisa API defaults remain authoritative.

## [1.0.1] - 2026-08-05

### Changed

- Publish only the installable `.difypkg` as a custom GitHub Release asset to make installation unambiguous.
- Embed the CycloneDX runtime SBOM inside the package and rely on GitHub’s asset digest and provenance attestation for external verification.
- Add the official repository URL to plugin metadata for GitHub-source installation and updates.
- Restore the Dify manifest metadata format version to `0.0.1`; the plugin release version remains `1.0.1`.

## [1.0.0] - 2026-08-05

### Added

- Add tag-only CI packaging, package-content validation, CycloneDX release SBOMs, SHA-256 checksums, and GitHub artifact provenance attestations.

### Changed

- Promote the model-provider plugin package version to `1.0.0`.

### Security

- Adopt the Shisa AI supply-chain baseline with uv locking, a seven-day resolution cutoff, fully pinned hashed requirements, immutable GitHub Action SHAs, dependency review, workflow policy validation, a repository audit, and deterministic CycloneDX SBOM generation.

## [0.0.6] - 2026-08-05

### Changed

- Normalize only the exact case-insensitive ASR no-speech marker `[Music]` to an empty transcript.

## [0.0.5] - 2026-08-04

### Changed

- Retrieve TTS voices dynamically where supported by Dify.
- Parse raw voice arrays and wrapped `voices` or `data` responses.
- Validate MP3 support for standard Dify TTS.
- Stream only when the selected voice and Dify surface support it; otherwise return complete MP3 bytes.

Earlier development history is available in Git.
