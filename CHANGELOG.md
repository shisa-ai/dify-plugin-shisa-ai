# Changelog

All notable user-visible changes are documented here.

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
