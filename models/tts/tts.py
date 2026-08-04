from collections.abc import Generator

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
    """Adapter for Shisa AI's streaming text-to-speech API."""

    def get_tts_model_voices(
        self, model: str, credentials: dict, language: str | None = None
    ) -> list[dict] | None:
        response = self._get_voices(credentials, validation=False)
        try:
            voices = response.json()
        except ValueError as error:
            raise InvokeBadRequestError("Shisa TTS returned an invalid voice list") from error

        result = []
        for item in voices:
            voice_id = item.get("id")
            if not voice_id:
                continue
            voice_language = str(item.get("language", ""))
            if language and language.split("-")[0].lower() not in voice_language.lower():
                continue
            result.append(
                {
                    "name": item.get("description") or voice_id,
                    "value": voice_id,
                }
            )
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
        if not content_text.strip():
            raise InvokeBadRequestError("Text-to-speech input must not be empty")

        if not voice:
            voices = self.get_tts_model_voices(model, credentials) or []
            if not voices:
                raise InvokeBadRequestError("No Shisa TTS voices are available")
            voice = voices[0]["value"]

        return self._stream_audio(credentials, content_text, voice)

    def validate_credentials(
        self, model: str, credentials: dict, user: str | None = None
    ) -> None:
        try:
            self._get_voices(credentials, validation=True)
        except CredentialsValidateFailedError:
            raise
        except Exception as error:
            raise CredentialsValidateFailedError(str(error)) from error

    def _stream_audio(
        self, credentials: dict, content_text: str, voice: str
    ) -> Generator[bytes, None, None]:
        api_base = credentials.get("api_base", "https://api.shisa.ai").rstrip("/")
        try:
            with httpx.stream(
                "POST",
                f"{api_base}/tts",
                headers={"Authorization": f"Bearer {credentials['api_key']}"},
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

    def _get_voices(self, credentials: dict, validation: bool) -> httpx.Response:
        api_key = credentials.get("api_key")
        if not api_key:
            raise CredentialsValidateFailedError("API key is required")
        api_base = credentials.get("api_base", "https://api.shisa.ai").rstrip("/")
        try:
            response = httpx.get(
                f"{api_base}/tts/voices",
                headers={"Authorization": f"Bearer {api_key}"},
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
        return response

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
