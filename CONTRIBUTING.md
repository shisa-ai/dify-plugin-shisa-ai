# Contributing

Thank you for helping improve the Shisa AI integration for Dify.

## Before opening a pull request

1. Open or reference an issue that describes the change.
2. Keep model-provider functionality in this repository; advanced workflow tools belong in the separate Tools repository.
3. Do not add undocumented claims about models, pricing, benchmarks, partnerships, security, availability, or Dify endorsement.
4. Use current official documentation from https://docs.shisa.ai/.
5. Never commit API keys, `.env`, `.dev.vars`, Dify application tokens, user data, remote-debug credentials, or generated `.difypkg` files.
6. Preserve existing Dify behavior notes, including synchronous workflow audio buffering and MP3 requirements for standard TTS.

## Validation

```bash
python3.12 -m venv .venv
. .venv/bin/activate
UV_EXCLUDE_NEWER=2026-07-29T00:00:00Z uv sync --frozen --no-install-project
uv run --frozen python -m compileall -q .
uv run --frozen python -m unittest discover -s tests -v
```

Also package and install the plugin in a test Dify workspace when changing provider behavior. Test affected LLM, ASR, or TTS paths without using production credentials in logs or fixtures.

## Pull requests

Keep changes focused, update `CHANGELOG.md`, and describe user-visible behavior and validation performed. Contributions are accepted under the [Apache License 2.0](LICENSE).
