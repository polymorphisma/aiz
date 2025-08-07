from abc import ABC, abstractmethod
from typing import Any


class UnifiedLanguageModel(ABC):
    """
    An abstract base class to provide a unified interface for various
    language model implementations. It enforces a common structure for
    initialization, lazy loading, and invocation.
    """

    def __init__(self, model_id: str, **kwargs: Any):
        """
        Initializes the unified model configuration.

        Args:
            model_id: The identifier for the specific model to be used.
            **kwargs: A dictionary for any additional configuration parameters
                      required by the specific implementation (e.g., api_key, region_name).
        """
        self.model_id = model_id
        self.model_parameters = kwargs
        self._llm: Any | None = None

    @abstractmethod
    def _initialize_llm(self) -> Any:
        """
        Abstract method for initializing the specific language model instance.
        Each subclass must implement this to create and configure its
        respective LLM object.
        """
        pass

    def _get_llm_instance(self) -> Any:
        """
        Lazily initializes and returns the language model instance.
        This method relies on the _initialize_llm method implemented by subclasses.
        """
        if self._llm is None:
            self._llm = self._initialize_llm()
        return self._llm

    # def invoke(self, messages: Any) -> Any:
    #     """
    #     Invokes the language model with the provided messages.

    #     Args:
    #         messages: The input messages for the model. The format can vary
    #                   depending on the underlying model's requirements.

    #     Returns:
    #         The response from the language model.
    #     """
    #     llm = self._get_llm_instance()
    #     return llm.invoke(messages)
