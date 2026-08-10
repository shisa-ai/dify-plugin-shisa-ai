#!/usr/bin/env python3
"""Automated Dify E2E for the Shisa AI Model Provider.

Covers the standard Dify interfaces:
  LLM   -> /v1/chat-messages   (Shisa V2.1 Flash)
  TTS   -> /v1/text-to-audio   (Shisa TTS, MP3)
  ASR   -> /v1/audio-to-text   (Shisa ASR via the workspace default model)

Also configures the provider credentials including the WORKSPACE-WIDE ASR
defaults (language + hotwords) and verifies the transcript reflects them.

Credentials are read from the environment (`.env.e2e` locally, GitHub release
environment secrets in CI) and are never printed.

Environment:
  DIFY_BASE_URL, DIFY_ADMIN_EMAIL, DIFY_ADMIN_PASSWORD, SHISA_API_KEY,
  MODEL_PKG_PATH, MODEL_DSL_PATH, AUDIO_PATH
"""

from __future__ import annotations

import base64
import json
import os
import sys
import time
from pathlib import Path

import httpx

MODEL_PROVIDER_FULL = "shisa-ai/shisa_ai/shisa_ai"
ASR_MODEL = "shisa-asr"
TTS_MODEL = "shisa-tts"
LLM_QUERY = "こんにちは、Shisa AIについて教えてください。"
TTS_TEXT = "Shisa AIの音声合成テストです。"


def _load_env_file(path: str = ".env.e2e") -> None:
    env_file = Path(path)
    if not env_file.is_file():
        return
    for raw in env_file.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"{name} is required")
    return value


def _wait(what: str, cond, timeout: float = 360.0, interval: float = 3.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if cond():
                return
        except Exception:
            pass
        time.sleep(interval)
    raise SystemExit(f"timeout waiting for {what}")


def _login(base: str, email: str, password: str) -> tuple[httpx.Client, dict[str, str]]:
    client = httpx.Client(base_url=base, timeout=120.0, follow_redirects=True)
    password_b64 = base64.b64encode(password.encode("utf-8")).decode("ascii")
    _wait("Dify API", lambda: client.get("/console/api/setup").status_code < 500)
    init = client.get("/console/api/init").json()
    if init.get("status") == "not_started":
        client.post("/console/api/init", json={"password": password})
    setup = client.get("/console/api/setup").json()
    if setup.get("step") == "not_started":
        client.post(
            "/console/api/setup",
            json={"email": email, "name": "admin", "password": password},
        )
    login = client.post(
        "/console/api/login",
        json={"email": email, "password": password_b64, "remember_me": True},
    )
    if login.status_code != 200:
        raise SystemExit(f"login failed ({login.status_code}): {login.text[:300]}")
    csrf = client.cookies.get("csrf_token")
    if not csrf:
        raise SystemExit("no csrf_token cookie after login")
    return client, {"X-CSRF-Token": csrf}


def _plugin_installed(client: httpx.Client, headers: dict[str, str], identifier: str) -> bool:
    response = client.get(
        "/console/api/workspaces/current/plugin/list", headers=headers
    )
    response.raise_for_status()
    payload = response.json()
    plugins = payload if isinstance(payload, list) else payload.get("plugins", [])
    return any(identifier in str(plugin) for plugin in plugins)


def _install(client: httpx.Client, headers: dict[str, str], pkg: Path, identifier: str) -> None:
    if _plugin_installed(client, headers, identifier):
        return
    with pkg.open("rb") as handle:
        upload = client.post(
            "/console/api/workspaces/current/plugin/upload/pkg",
            headers=headers,
            files={"pkg": (pkg.name, handle, "application/octet-stream")},
        )
    upload.raise_for_status()
    upload_identifier = upload.json().get("unique_identifier") or identifier
    install = client.post(
        "/console/api/workspaces/current/plugin/install/pkg",
        headers=headers,
        json={"plugin_unique_identifiers": [upload_identifier]},
    )
    install.raise_for_status()
    if not install.json().get("all_installed"):
        _wait(
            "model plugin install",
            lambda: _plugin_installed(client, headers, upload_identifier),
        )


def main() -> int:
    base = _env("DIFY_BASE_URL").rstrip("/")
    email = _env("DIFY_ADMIN_EMAIL")
    password = _env("DIFY_ADMIN_PASSWORD")
    shisa_key = _env("SHISA_API_KEY")
    pkg = Path(_env("MODEL_PKG_PATH"))
    dsl = Path(_env("MODEL_DSL_PATH"))
    audio = Path(_env("AUDIO_PATH"))
    if not pkg.is_file() or not dsl.is_file() or not audio.is_file():
        raise SystemExit("MODEL_PKG_PATH, MODEL_DSL_PATH, AUDIO_PATH must be existing files")

    client, headers = _login(base, email, password)

    # Install the Model Provider plugin.
    with pkg.open("rb") as handle:
        probe = client.post(
            "/console/api/workspaces/current/plugin/upload/pkg",
            headers=headers,
            files={"pkg": (pkg.name, handle, "application/octet-stream")},
        )
    probe.raise_for_status()
    identifier = probe.json().get("unique_identifier")
    _install(client, headers, pkg, identifier)

    # Configure provider credentials with WORKSPACE-WIDE ASR defaults.
    creds = client.post(
        f"/console/api/workspaces/current/model-providers/{MODEL_PROVIDER_FULL}/credentials",
        headers=headers,
        json={
            "credentials": {
                "api_key": shisa_key,
                "api_base": "https://api.shisa.ai",
                "asr_language": "ja",
                "asr_hotwords": '["Shisa AI","Shisa V2.1","Dify"]',
            },
            "name": "release-e2e",
        },
    )
    if creds.status_code >= 400 and creds.status_code != 409 and "already used" not in creds.text and "already exists" not in creds.text:
        creds.raise_for_status()

    # Set the workspace default Speech2Text and TTS models.
    defaults = client.post(
        "/console/api/workspaces/current/default-model",
        headers=headers,
        json={
            "model_settings": [
                {"model_type": "speech2text", "provider": MODEL_PROVIDER_FULL, "model": ASR_MODEL},
                {"model_type": "tts", "provider": MODEL_PROVIDER_FULL, "model": TTS_MODEL},
            ]
        },
    )
    if defaults.status_code >= 400:
        defaults.raise_for_status()

    # Import the chat app DSL and publish it.
    imported = client.post(
        "/console/api/apps/imports",
        headers=headers,
        json={
            "mode": "yaml-content",
            "yaml_content": dsl.read_text(encoding="utf-8"),
            "name": "Shisa Model Provider E2E",
        },
    )
    if imported.status_code == 202:
        import_id = imported.json().get("id")
        _wait(
            "dsl import confirm",
            lambda: client.post(
                f"/console/api/apps/imports/{import_id}/confirm", headers=headers
            ).status_code
            in (200, 400),
        )
        imported = client.post(
            f"/console/api/apps/imports/{import_id}/confirm", headers=headers
        )
    imported.raise_for_status()
    app_id = imported.json().get("app_id")
    if not app_id:
        raise SystemExit(f"no app_id from import: {json.dumps(imported.json())[:400]}")

    client.post(f"/console/api/apps/{app_id}/api-enable", headers=headers)
    key_response = client.post(f"/console/api/apps/{app_id}/api-keys", headers=headers)
    key_response.raise_for_status()
    app_token = key_response.json().get("token")
    app_headers = {"Authorization": f"Bearer {app_token}"}

    # LLM
    chat = client.post(
        "/v1/chat-messages",
        headers=app_headers,
        json={"inputs": {}, "query": LLM_QUERY, "response_mode": "blocking", "user": "e2e"},
        timeout=180,
    )
    chat.raise_for_status()
    answer = str(chat.json().get("answer", "")).strip()
    if not answer:
        raise SystemExit("LLM returned an empty answer")

    # TTS
    tts = client.post(
        "/v1/text-to-audio",
        headers=app_headers,
        json={"text": TTS_TEXT, "user": "e2e"},
        timeout=180,
    )
    tts.raise_for_status()
    if len(tts.content) < 1000:
        raise SystemExit(f"TTS returned too little audio: {len(tts.content)} bytes")

    # ASR (workspace default Speech2Text with WORKSPACE-WIDE hotwords)
    with audio.open("rb") as handle:
        asr = client.post(
            "/v1/audio-to-text",
            headers=app_headers,
            data={"user": "e2e"},
            files={"file": (audio.name, handle, "audio/wav")},
            timeout=180,
        )
    asr.raise_for_status()
    transcript = str(asr.json().get("text", "")).strip()
    if not transcript:
        raise SystemExit("ASR returned an empty transcript")
    if "シサAI" in transcript:
        raise SystemExit(f"non-preferred brand spelling in transcript: {transcript!r}")

    report = {
        "status": "succeeded",
        "llm": {"status": "pass", "answer_chars": len(answer)},
        "tts": {"status": "pass", "bytes": len(tts.content)},
        "asr": {
            "status": "pass",
            "workspace_defaults": ["asr_language=ja", "asr_hotwords"],
            "text": transcript,
        },
        "app_id": app_id,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    _load_env_file()
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"model provider e2e failed: {error}", file=sys.stderr)
        raise SystemExit(1)
