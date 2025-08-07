from typing import Any

from langchain_aws import ChatBedrockConverse

from .base_provider import UnifiedLanguageModel
from .providers_exception import ModelConfigurationError


class AwsBedrockModel(UnifiedLanguageModel):
    """
    A unified wrapper for the LangChain ChatBedrockConverse class.

    This class standardizes access to AWS Bedrock models via the Converse API.
    """

    def __init__(self, model_id: str, **kwargs: Any):
        """
        Initializes the AWS Bedrock model wrapper.

        Args:
            model_id: The Bedrock model ID (e.g., 'anthropic.claude-3-haiku-20240307-v1:0').
            **kwargs: Required AWS credentials and other model parameters:
                - aws_access_key_id (str): Required.
                - aws_secret_access_key (str): Required.
                - aws_session_token (str, optional)
                - region_name (str, optional, default='us-east-1')
                - system (str, optional): System prompt.
                - Other model parameters (temperature, max_tokens, etc.)
        """
        super().__init__(model_id, **kwargs)

        # Validation
        if 'aws_access_key_id' not in self.model_parameters or 'aws_secret_access_key' not in self.model_parameters:
            raise ModelConfigurationError('Both aws_access_key_id and aws_secret_access_key must be provided.')

        # Format system prompt if given
        system = self.model_parameters.get('system')
        self.system_prompt = [{'text': system}] if system else None

    def _initialize_llm(self) -> ChatBedrockConverse:
        """
        Creates and returns a lazily-initialized ChatBedrockConverse instance.
        """
        return ChatBedrockConverse(
            model=self.model_id,
            aws_access_key_id=self.model_parameters['aws_access_key_id'],
            aws_secret_access_key=self.model_parameters['aws_secret_access_key'],
            aws_session_token=self.model_parameters.get('aws_session_token'),
            region_name=self.model_parameters.get('region_name', 'us-east-1'),
            system=self.system_prompt,
            **{
                k: v for k, v in self.model_parameters.items()
                if k not in {'aws_access_key_id', 'aws_secret_access_key', 'aws_session_token', 'region_name', 'system'}
            }
        )
