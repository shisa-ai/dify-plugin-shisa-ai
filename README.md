# Shisa AI provider for Dify

A Dify model-provider plugin for Shisa AI's Japanese and English services:

- Shisa V2.1 Flash and Pro LLMs
- Shisa ASR speech recognition
- Shisa TTS speech synthesis with dynamically discovered voices

## API key

Create a Shisa AI account and obtain an API key at [platform.shisa.ai](https://platform.shisa.ai/).

## Development

This plugin requires Python 3.12.

```bash
cp .env.example .env
python3.12 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m main
```

Use the debug host and key shown in your Dify Cloud workspace's plugin debug dialog.

## Package

```bash
dify plugin package .
```

## Service endpoints

By default, the plugin calls:

- LLM: `https://api.shisa.ai/openai/v1/chat/completions`
- ASR: `https://api.shisa.ai/asr/srt/audio_llm`
- TTS: `https://api.shisa.ai/tts`
- Voices: `https://api.shisa.ai/tts/voices`
