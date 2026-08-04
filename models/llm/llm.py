from collections.abc import Generator

from dify_plugin import OAICompatLargeLanguageModel
from dify_plugin.entities.model.llm import LLMResult
from dify_plugin.entities.model.message import PromptMessage, PromptMessageTool


class ShisaAILargeLanguageModel(OAICompatLargeLanguageModel):
    """OpenAI-compatible adapter for Shisa AI language models."""

    def _invoke(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        model_parameters: dict,
        tools: list[PromptMessageTool] | None = None,
        stop: list[str] | None = None,
        stream: bool = True,
        user: str | None = None,
    ) -> LLMResult | Generator:
        adapted = self._adapt_credentials(credentials)
        return super()._invoke(
            model,
            adapted,
            prompt_messages,
            model_parameters,
            tools,
            stop,
            stream,
            user,
        )

    def validate_credentials(self, model: str, credentials: dict) -> None:
        super().validate_credentials(model, self._adapt_credentials(credentials))

    @staticmethod
    def _adapt_credentials(credentials: dict) -> dict:
        adapted = dict(credentials)
        api_base = adapted.get("api_base", "https://api.shisa.ai").rstrip("/")
        adapted["mode"] = "chat"
        adapted["endpoint_url"] = f"{api_base}/openai/v1"
        return adapted
