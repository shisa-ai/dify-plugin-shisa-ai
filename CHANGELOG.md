# Changelog

All notable user-visible changes are documented here.

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
