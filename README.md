# Shisa AI Model Provider for Dify

A Dify model-provider plugin for connecting Dify applications directly to Shisa AI's Japanese and English APIs.

> This repository is maintained by Shisa AI. It does not imply certification, endorsement, or support by Dify unless separately stated by Dify.

## Supported interfaces

| Dify interface | Shisa service | Notes |
| --- | --- | --- |
| LLM | Shisa V2.1 Flash and Pro | OpenAI-compatible chat completions |
| Speech-to-Text | Shisa ASR | Exact no-speech marker `[Music]` is normalized to an empty transcript |
| Text-to-Speech | Shisa TTS | Standard Dify integration outputs MP3 and discovers voices dynamically where Dify supports it |

Translation is exposed separately through [Shisa AI Tools for Dify](https://github.com/shisa-ai/dify-plugin-shisa-ai-tools), because Dify does not provide a standard Translation model-provider interface.

## Requirements

- A Shisa AI account and API key from [Shisa Platform](https://platform.shisa.ai/)
- A Dify installation that supports model-provider plugins
- Python 3.12 for local development

Current prices, quotas, model availability, and account-specific rates can change. Check [Shisa Platform](https://platform.shisa.ai/) and the [official API documentation](https://docs.shisa.ai/) for current information rather than relying on repository snapshots.

## Installation

1. Download `shisa-ai-1.0.1.difypkg` from the [v1.0.0 GitHub Release](https://github.com/shisa-ai/dify-plugin-shisa-ai/releases/tag/v1.0.1).
2. Optionally verify its GitHub-provided SHA-256 digest and provenance attestation.
3. In Dify, open **Plugins**, choose installation from a local package, and upload the file.
4. Open the Shisa AI model-provider settings and enter your Shisa AI API key.
5. Select the required Shisa LLM, ASR, or TTS model in your Dify application.

Only the `.difypkg` file is installable in Dify. GitHub’s automatically generated **Source code (zip)** and **Source code (tar.gz)** archives are not plugin packages.

Do not commit API keys or Dify remote-debug credentials.

## Dify behavior and limitations

- Standard Dify TTS uses MP3 because Dify's application audio endpoint expects `audio/mpeg`.
- Dify Workflow TTS and Tool nodes buffer completed files before downstream nodes receive them; they do not provide progressive workflow playback.
- Some Dify surfaces can retrieve voices dynamically, while workflow selectors may rely on packaged fallback metadata.
- Actual TTS formats and streaming support vary by voice. `GET /tts/voices` is the source of truth.
- Silent or wrong-microphone input may be returned by the ASR service as the exact marker `[Music]`; this plugin converts only that exact case-insensitive marker to an empty transcript.

For native audio formats and dynamic voice tooling, use the separate [Shisa AI Tools plugin](https://github.com/shisa-ai/dify-plugin-shisa-ai-tools).

## Development

```bash
cp .env.example .env
python3.12 -m venv .venv
. .venv/bin/activate
uv sync --frozen --no-install-project
uv run --frozen python main.py
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
uv sync --frozen --no-install-project
uv run --frozen python main.py
```

Use the debug host and temporary key shown in the Dify plugin-debug dialog. Never publish `.env`, `.dev.vars`, application tokens, or remote-debug keys.

## Package

With the Dify plugin CLI installed:

```bash
dify plugin package .
```

Protected `v*` tags invoke `.github/workflows/release.yml`. CI builds and validates the `.difypkg`, embeds a runtime SBOM, attests provenance, and publishes only the installable package to the matching GitHub Release. Generated release files are intentionally excluded from Git.

## Service endpoints

- LLM: `https://api.shisa.ai/openai/v1/chat/completions`
- ASR: `https://api.shisa.ai/asr/srt/audio_llm`
- TTS: `https://api.shisa.ai/tts`
- Voices: `https://api.shisa.ai/tts/voices`

## License

Licensed under the [Apache License 2.0](LICENSE).

## Security and privacy

- Report vulnerabilities according to [SECURITY.md](SECURITY.md).
- Data-handling details are documented in [PRIVACY.md](PRIVACY.md).
- Contributions are described in [CONTRIBUTING.md](CONTRIBUTING.md).
