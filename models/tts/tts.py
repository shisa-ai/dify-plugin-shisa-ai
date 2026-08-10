from collections.abc import Generator
from typing import Any

import httpx
from dify_plugin import TTSModel
from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeConnectionError,
    InvokeError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)


class ShisaAIText2SpeechModel(TTSModel):
    """Adapter for Shisa AI's native MP3 text-to-speech API."""

    def get_tts_model_voices(
        self, model: str, credentials: dict, language: str | None = None
    ) -> list[dict] | None:
        """Fetch the current MP3-capable voice catalogue from Shisa AI."""
        voices = self._get_voice_catalog(credentials)
        result = []
        for item in voices:
            if not self._supports_format(item, "mp3"):
                continue
            if language and not self._supports_language(item, language):
                continue
            voice_id = str(item.get("id", "")).strip()
            if not voice_id:
                continue
            result.append({"name": self._voice_name(item), "value": voice_id})
        return result

    def _invoke(
        self,
        model: str,
        tenant_id: str,
        credentials: dict,
        content_text: str,
        voice: str,
        user: str | None = None,
    ) -> bytes | Generator[bytes, None, None]:
        text = content_text.strip()
        if not text:
            raise InvokeBadRequestError("Text-to-speech input must not be empty")

        catalog = self._get_voice_catalog(credentials)
        selected = self._select_voice(catalog, voice)
        voice_id = str(selected["id"])
        if not self._supports_format(selected, "mp3"):
            raise InvokeBadRequestError(
                f"Voice {voice_id} does not support MP3, which Dify's standard TTS interface requires"
            )

        if selected.get("streaming") is True:
            return self._stream_audio(credentials, text, voice_id)
        return self._generate_audio(credentials, text, voice_id)

    def validate_credentials(
        self, model: str, credentials: dict, user: str | None = None
    ) -> None:
        try:
            self._get_voice_catalog(credentials, validation=True)
        except CredentialsValidateFailedError:
            raise
        except Exception as error:
            raise CredentialsValidateFailedError(str(error)) from error

    def _stream_audio(
        self, credentials: dict, content_text: str, voice: str
    ) -> Generator[bytes, None, None]:
        try:
            with httpx.stream(
                "POST",
                self._tts_url(credentials),
                headers=self._headers(credentials),
                json={
                    "voice_id": voice,
                    "format": "mp3",
                    "stream": True,
                    "text": content_text,
                },
                timeout=300.0,
            ) as response:
                self._raise_for_status(response)
                yielded = False
                for chunk in response.iter_bytes():
                    if chunk:
                        yielded = True
                        yield chunk
                if not yielded:
                    raise InvokeBadRequestError("Shisa TTS returned no audio data")
        except (httpx.ConnectError, httpx.TimeoutException) as error:
            raise InvokeConnectionError(str(error)) from error

    def _generate_audio(self, credentials: dict, content_text: str, voice: str) -> bytes:
        try:
            response = httpx.post(
                self._tts_url(credentials),
                headers=self._headers(credentials),
                json={
                    "voice_id": voice,
                    "format": "mp3",
                    "stream": False,
                    "text": content_text,
                },
                timeout=300.0,
            )
            self._raise_for_status(response)
            if not response.content:
                raise InvokeBadRequestError("Shisa TTS returned no audio data")
            return response.content
        except (httpx.ConnectError, httpx.TimeoutException) as error:
            raise InvokeConnectionError(str(error)) from error

    def _get_voice_catalog(
        self, credentials: dict, validation: bool = False
    ) -> list[dict[str, Any]]:
        key = credentials.get("api_key")
        if not key:
            if validation:
                raise CredentialsValidateFailedError("API key is required")
            raise InvokeAuthorizationError("API key is required")

        try:
            response = httpx.get(
                f"{self._api_base(credentials)}/tts/voices",
                headers=self._headers(credentials),
                timeout=30.0,
            )
        except (httpx.ConnectError, httpx.TimeoutException) as error:
            if validation:
                raise CredentialsValidateFailedError(str(error)) from error
            raise InvokeConnectionError(str(error)) from error

        if validation and response.status_code >= 400:
            raise CredentialsValidateFailedError(
                f"Shisa AI rejected the credentials ({response.status_code}): {response.text}"
            )
        self._raise_for_status(response)

        try:
            payload = response.json()
        except ValueError as error:
            message = "Shisa TTS returned an invalid voice catalogue"
            if validation:
                raise CredentialsValidateFailedError(message) from error
            raise InvokeBadRequestError(message) from error

        if isinstance(payload, list):
            voices = payload
        elif isinstance(payload, dict):
            voices = payload.get("voices", payload.get("data", []))
        else:
            voices = []

        if not isinstance(voices, list):
            voices = []
        result = [item for item in voices if isinstance(item, dict) and item.get("id")]
        if not result:
            message = "Shisa TTS returned an empty voice catalogue"
            if validation:
                raise CredentialsValidateFailedError(message)
            raise InvokeBadRequestError(message)
        return result

    @staticmethod
    def _select_voice(catalog: list[dict[str, Any]], voice: str) -> dict[str, Any]:
        if voice:
            for item in catalog:
                if str(item.get("id")) == voice:
                    return item
            raise InvokeBadRequestError(f"Shisa TTS voice not found: {voice}")

        for item in catalog:
            if ShisaAIText2SpeechModel._supports_format(item, "mp3"):
                return item
        raise InvokeBadRequestError("No MP3-capable Shisa TTS voices are available")

    @staticmethod
    def _supports_format(voice: dict[str, Any], audio_format: str) -> bool:
        formats = voice.get("formats", [])
        return isinstance(formats, list) and audio_format.lower() in {
            str(value).lower() for value in formats
        }

    @staticmethod
    def _supports_language(voice: dict[str, Any], language: str) -> bool:
        requested = language.split("-")[0].lower()
        aliases = {"ja": "japanese", "en": "english", "zh": "chinese"}
        requested = aliases.get(requested, requested)
        available = str(voice.get("language", "")).lower()
        return not available or requested in available

    @staticmethod
    def _voice_name(voice: dict[str, Any]) -> str:
        return str(
            voice.get("displayName")
            or voice.get("name")
            or voice.get("description")
            or voice["id"]
        )

    @staticmethod
    def _api_base(credentials: dict) -> str:
        return str(credentials.get("api_base", "https://api.shisa.ai")).rstrip("/")

    @classmethod
    def _tts_url(cls, credentials: dict) -> str:
        return f"{cls._api_base(credentials)}/tts"

    @staticmethod
    def _headers(credentials: dict) -> dict[str, str]:
        return {"Authorization": f"Bearer {credentials['api_key']}"}

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.status_code in (401, 403):
            raise InvokeAuthorizationError(response.text)
        if response.status_code == 429:
            raise InvokeRateLimitError(response.text)
        if response.status_code >= 500:
            raise InvokeServerUnavailableError(response.text)
        if response.status_code >= 400:
            raise InvokeBadRequestError(response.text)

    @property
    def _invoke_error_mapping(self) -> dict[type[InvokeError], list[type[Exception]]]:
        return {
            InvokeConnectionError: [httpx.ConnectError, httpx.TimeoutException],
            InvokeAuthorizationError: [],
            InvokeRateLimitError: [],
            InvokeServerUnavailableError: [],
            InvokeBadRequestError: [httpx.HTTPError],
        }
