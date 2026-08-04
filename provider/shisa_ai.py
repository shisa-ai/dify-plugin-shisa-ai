import logging

from dify_plugin import ModelProvider
from dify_plugin.entities.model import ModelType
from dify_plugin.errors.model import CredentialsValidateFailedError

logger = logging.getLogger(__name__)


class ShisaAIProvider(ModelProvider):
    def validate_provider_credentials(self, credentials: dict) -> None:
        """Validate the shared Shisa AI API key with the inexpensive voices endpoint."""
        try:
            model_instance = self.get_model_instance(ModelType.TTS)
            model_instance.validate_credentials(model="shisa-tts", credentials=credentials)
        except CredentialsValidateFailedError:
            raise
        except Exception as error:
            logger.exception("Shisa AI credentials validation failed")
            raise CredentialsValidateFailedError(str(error)) from error
