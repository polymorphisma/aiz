from typing import Any

from langchain_anthropic import ChatAnthropic

from .base_provider import UnifiedLanguageModel
from .providers_exception import ModelConfigurationError


class AnthropicChatModel(UnifiedLanguageModel):
    """
    A unified wrapper for the LangChain ChatAnthropic class.

    This class provides a standardized interface for using Anthropic's models
    (e.g., Claude 3) within the unified model framework.
    """

    def __init__(self, model_id: str, **kwargs: Any):
        """
        Initializes the AnthropicChatModel wrapper.

        Args:
            model_id: The ID of the Anthropic model to use (e.g., 'claude-3-sonnet-20240229').
            **kwargs: Additional parameters, which must include 'api_key' and can
                      also contain 'temperature', 'max_tokens', etc.
        """
        super().__init__(model_id, **kwargs)

        if 'api_key' not in self.model_parameters:
            raise ModelConfigurationError(
                "An 'api_key' must be provided in the keyword arguments for AnthropicChatModel."
            )

    def _initialize_llm(self) -> ChatAnthropic:
        """
        Implements the abstract method to initialize the ChatAnthropic instance.

        This method is called by the lazy loader (_get_llm_instance) when the model
        is first accessed.

        Returns:
            An instance of the LangChain ChatAnthropic class.
        """

        return ChatAnthropic(model=self.model_id, **self.model_parameters)
