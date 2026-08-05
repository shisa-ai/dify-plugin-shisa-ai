import base64
import json
from typing import IO, Any

import httpx
from dify_plugin import Speech2TextModel
from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeConnectionError,
    InvokeError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)


class ShisaAISpeech2TextModel(Speech2TextModel):
    """Adapter for Shisa AI's base64 JSON speech-recognition API."""

    def _invoke(
        self,
        model: str,
        credentials: dict,
        file: IO[bytes],
        user: str | None = None,
    ) -> str:
        audio = file.read()
        if not audio:
            raise InvokeBadRequestError("The audio file is empty")

        payload: dict[str, Any] = {
            "audio": base64.b64encode(audio).decode("ascii")
        }
        payload.update(self._workspace_asr_defaults(credentials))
        response = self._request(credentials, payload)
        try:
            result = response.json()
            text = result["text"]
        except (ValueError, KeyError, TypeError) as error:
            raise InvokeBadRequestError("Shisa ASR returned an invalid response") from error
        return self._normalize_transcript(str(text))

    @classmethod
    def _workspace_asr_defaults(cls, credentials: dict) -> dict[str, Any]:
        """Parse explicitly configured workspace-wide ASR request defaults."""
        defaults: dict[str, Any] = {}

        language = str(credentials.get("asr_language") or "").strip()
        if language:
            defaults["language"] = language

        raw_hotwords = str(credentials.get("asr_hotwords") or "").strip()
        if raw_hotwords:
            defaults["hotwords"] = cls._parse_hotwords(raw_hotwords)

        float_fields = {
            "asr_temperature": "temperature",
            "asr_top_p": "top_p",
            "asr_frequency_penalty": "frequency_penalty",
            "asr_repetition_penalty": "repetition_penalty",
        }
        for credential_name, api_name in float_fields.items():
            raw_value = str(credentials.get(credential_name) or "").strip()
            if raw_value:
                try:
                    defaults[api_name] = float(raw_value)
                except ValueError as error:
                    raise InvokeBadRequestError(
                        f"Workspace-wide {credential_name} must be a number"
                    ) from error

        raw_vad = str(credentials.get("asr_vad") or "").strip()
        if raw_vad:
            try:
                defaults["vad"] = int(raw_vad)
            except ValueError as error:
                raise InvokeBadRequestError(
                    "Workspace-wide asr_vad must be an integer"
                ) from error

        return defaults

    @staticmethod
    def _parse_hotwords(value: str) -> list[str]:
        """Accept a JSON string array or a newline/comma-separated list."""
        if value.lstrip().startswith("["):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError as error:
                raise InvokeBadRequestError(
                    "Workspace-wide ASR hotwords must be valid JSON or a newline/comma-separated list"
                ) from error
            if not isinstance(parsed, list) or not all(
                isinstance(item, str) for item in parsed
            ):
                raise InvokeBadRequestError(
                    "Workspace-wide ASR hotwords JSON must be an array of strings"
                )
            hotwords = [item.strip() for item in parsed if item.strip()]
        else:
            hotwords = [
                item.strip()
                for line in value.splitlines()
                for item in line.split(",")
                if item.strip()
            ]
        if not hotwords:
            raise InvokeBadRequestError(
                "Workspace-wide ASR hotwords must contain at least one word or phrase"
            )
        return hotwords

    @staticmethod
    def _normalize_transcript(text: str) -> str:
        """Do not insert Shisa's exact no-speech music marker into user input."""
        transcript = text.strip()
        if transcript.casefold() == "[music]":
            return ""
        return transcript

    def validate_credentials(self, model: str, credentials: dict) -> None:
        # Provider-level validation uses GET /tts/voices and does not consume ASR credits.
        if not credentials.get("api_key"):
            raise CredentialsValidateFailedError("API key is required")

    @staticmethod
    def _request(credentials: dict, payload: dict) -> httpx.Response:
        api_base = credentials.get("api_base", "https://api.shisa.ai").rstrip("/")
        try:
            response = httpx.post(
                f"{api_base}/asr/srt/audio_llm",
                headers={"Authorization": f"Bearer {credentials['api_key']}"},
                json=payload,
                timeout=300.0,
            )
        except (httpx.ConnectError, httpx.TimeoutException) as error:
            raise InvokeConnectionError(str(error)) from error

        if response.status_code in (401, 403):
            raise InvokeAuthorizationError(response.text)
        if response.status_code == 429:
            raise InvokeRateLimitError(response.text)
        if response.status_code >= 500:
            raise InvokeServerUnavailableError(response.text)
        if response.status_code >= 400:
            raise InvokeBadRequestError(response.text)
        return response

    @property
    def _invoke_error_mapping(self) -> dict[type[InvokeError], list[type[Exception]]]:
        return {
            InvokeConnectionError: [httpx.ConnectError, httpx.TimeoutException],
            InvokeAuthorizationError: [],
            InvokeRateLimitError: [],
            InvokeServerUnavailableError: [],
            InvokeBadRequestError: [httpx.HTTPError],
        }
