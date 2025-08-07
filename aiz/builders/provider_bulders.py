from typing import Dict, Any, Type

from ..providers import AnthropicChatModel, AwsBedrockModel, ModelConfigurationError, UnifiedLanguageModel

class ProviderFactory:
    """
    A factory class responsible for creating language model instances based on
    a provider name. It acts as a router to the correct model builder class.
    """
    def __init__(self):
        self._build_map: Dict[str, Type[UnifiedLanguageModel]] = {
            "anthropic": AnthropicChatModel,
            "aws_bedrock": AwsBedrockModel,
        }

    def _get_builder_class(self, provider: str) -> Type[UnifiedLanguageModel]:
        """
        Retrieves the correct builder class from the map.
        
        Raises:
            ModelConfigurationError: If the provider is not supported.
        """
        builder_class = self._build_map.get(provider.lower())
        if builder_class is None:
            raise ModelConfigurationError(
                f"Unsupported model provider: '{provider}'. "
                f"Supported providers are: {list(self._build_map.keys())}"
            )
        return builder_class

    def build(self, config: Dict[str, Any]) -> Any:
        """
        Builds and returns a runnable language model instance from a configuration dictionary.

        The configuration dictionary must contain:
        - 'provider': A string key identifying the model provider (e.g., 'anthropic').
        - 'model_id': The specific model ID to use.
        - Other provider-specific arguments (e.g., api_key, region_name).

        Args:
            config: The configuration dictionary for the model.

        Returns:
            A runnable LangChain LLM instance.
        """
        provider = config.get("provider")
        if not provider:
            raise ModelConfigurationError("Configuration must include a 'provider' key.")

        BuilderClass = self._get_builder_class(provider)

        init_args = config.copy()
        init_args.pop("provider")
        
        try:
            model_wrapper = BuilderClass(**init_args)
            
            return model_wrapper._get_llm_instance()
        
        except TypeError as e:
            raise ModelConfigurationError(
                f"Failed to initialize model for provider '{provider}'. "
                f"Please check the provided arguments. Error: {e}"
            )
        except Exception as e:
            raise e


if __name__ == "__main__":
    provider_config = {
        "provider": "aws_bedrock",
    }