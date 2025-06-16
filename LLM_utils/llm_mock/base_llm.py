from abc import ABC
import logging


class MockLLM(ABC):
    """Base class for all LLM classes. It defines the API to use the LLMs, but this mock version raises NotImplementedError for all methods."""

    def __init__(self, prompt_token_cost: float = 0, response_token_cost: float = 0, max_tokens: int = 0,
                 max_tokens_ratio_per_input: float = 0.7):
        """Constructor for the MockLLM class
        Args:
            prompt_token_cost (float): Cost of a token in the prompt
            response_token_cost (float): Cost of a token in the response
            max_tokens (int): Maximum number of tokens
            max_tokens_ratio_per_input (float): Maximum ratio of tokens per input in the prompt, to avoid the LLM using all tokens in the prompt for just the input
        """
        pass

    def _calculate_tokens(self, prompt: str) -> int:
        """Method for calculating the number of tokens in the prompt.
        Args:
            prompt (str): Prompt
        Raises:
            NotImplementedError: This method is not implemented in the mock class.
        """
        raise NotImplementedError("This method is not implemented in the MockLLM class.")

    def _update_costs(self, prompt_tokens: int, response_tokens: int):
        """Update the cost of the prompt and response.
        Args:
            prompt_tokens (int): Number of tokens in the prompt
            response_tokens (int): Number of tokens in the response
        Raises:
            NotImplementedError: This method is not implemented in the mock class.
        """
        raise NotImplementedError("This method is not implemented in the MockLLM class.")

    @staticmethod
    def retry_with_exponential_backoff(
            func,
            logger: logging.Logger,
            errors: tuple,
            initial_delay: float = 1,
            exponential_base: float = 1,
            jitter: bool = True,
            max_retries: int = 10,
    ):
        """Retry a function with exponential backoff.
        Args:
            func (function): Function to retry
            logger (logging.Logger): Logger
            errors (tuple): Tuple of type of errors to retry
            initial_delay (float, optional): Initial delay. Defaults to 1.
            exponential_base (float, optional): Exponential base. Defaults to 2.
            jitter (bool, optional): Add jitter to the delay. Defaults to True.
            max_retries (int, optional): Maximum number of retries. Defaults to 5.

        Raises:
            NotImplementedError: This method is not implemented in the mock class.
        """
        raise NotImplementedError("This static method is not implemented in the MockLLM class.")

    def _completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Method for the completion API.
        Args:
            prompt (str): Prompt for the completion
        Raises:
            NotImplementedError: This method is not implemented in the mock class.
        """
        raise NotImplementedError("This method is not implemented in the MockLLM class.")

    def _load_prompt(self, prompt: str) -> str:
        """Load the prompt from a file or return the prompt if it is a string.
        Args:
            prompt (str): Prompt file or string
        Raises:
            NotImplementedError: This method is not implemented in the mock class.
        """
        raise NotImplementedError("This method is not implemented in the MockLLM class.")

    def _replace_inputs_in_prompt(self, prompt: str, inputs: list[str] = []) -> str:
        """Replace the inputs in the prompt.
        Args:
            prompt (str): Prompt. For example: "This is a <input1> prompt with <input2> two inputs"
            inputs (list[str]): List of inputs
        Raises:
            NotImplementedError: This method is not implemented in the mock class.
        """
        raise NotImplementedError("This method is not implemented in the MockLLM class.")

    def completion(self, prompt: str, **kwargs) -> str:
        """Method for the completion API.
        Args:
            prompt (str): Prompt file or string for the completion
        Raises:
            NotImplementedError: This method is not implemented in the mock class.
        """
        raise NotImplementedError("This method is not implemented in the MockLLM class.")