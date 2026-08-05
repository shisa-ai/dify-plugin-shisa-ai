import base64
from typing import IO

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

        response = self._request(
            credentials,
            {"audio": base64.b64encode(audio).decode("ascii")},
        )
        try:
            result = response.json()
            text = result["text"]
        except (ValueError, KeyError, TypeError) as error:
            raise InvokeBadRequestError("Shisa ASR returned an invalid response") from error
        return self._normalize_transcript(str(text))

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
