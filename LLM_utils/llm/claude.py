import os
from typing import List

from .base_llm import BaseLLM
import anthropic
from anthropic import Anthropic
import tiktoken


class CLAUDE_3_5_SONNET(BaseLLM):
    """Class for the claude-3-5-sonnet model from Anthropic with 4000 tokens of context"""

    def __init__(self):
        """Constructor for the CLAUDE_3_5_SONNET class
        Args:
            prompt_token_cost (float): Cost of a token in the prompt
            response_token_cost (float): Cost of a token in the response
        """
        super().__init__(0.0003 / 1000, 0.0015 / 1000, 8192, 0.7)

        self.logger.debug("Loading claude-3-5-sonnet model from Anthropic API...")
        # Load the GPT-3.5 model
        self.client = Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )
        self.deployment_name = os.getenv("CLAUDE_3_5_SONNET_MODEL_ID")
        # Encoding to estimate the number of tokens
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0125")

        self.logger.debug("claude-3-5-sonnet model loaded")

    def _format_prompt(self, prompt: str, role: str = 'user') -> list[dict[str, str]]:
        """Format the prompt to be used by the GPT-3.5 model
        Args:
            prompt (str): Prompt
        Returns:
            list: List of dictionaries containing the prompt and the role of the speaker
        """
        return [
            {"content": prompt, "role": role}
        ]

    def __completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Completion api for the GPT-3.5 model
        Args:
            prompt (str): Prompt for the completion
        Returns:
            tuple(str, int, int): A tuple with the completed text, the number of tokens in the prompt and the number of tokens in the response
        """
        prompt = self._format_prompt(prompt)

        if "system_prompt" in kwargs:
            system_prompt = kwargs["system_prompt"]
            del kwargs["system_prompt"]
        else:
            system_prompt = None
        if "seed" in kwargs:
            del kwargs["seed"] 

        response = self.client.messages.create(model=self.deployment_name, system=system_prompt,
                                               messages=prompt, max_tokens=self.max_tokens, **kwargs)

        try:
            completion = response.content[0].text
            prompt_tokens = response.usage.input_tokens
            response_tokens = response.usage.output_tokens
        except Exception as e:
            print(response)
            raise

        return completion, prompt_tokens, response_tokens

    def _completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Wrapper for the completion api with retry and exponential backoff

        Args:
            prompt (str): Prompt for the completion

        Returns:
            tuple(str, int, int): A tuple with the completed text, the number of tokens in the prompt and the number of tokens in the response
        """
        wrapper = BaseLLM.retry_with_exponential_backoff(self.__completion, self.logger, errors=(
            anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.InternalServerError))
        return wrapper(prompt, **kwargs)

    def _calculate_tokens(self, prompt: str) -> int:
        """Calculate the number of tokens in the prompt
        Args:
            prompt (str): Prompt
        Returns:
            int: Number of tokens in the prompt
        """

        num_tokens = 0
        num_tokens += len(self.encoding.encode(prompt))
        return num_tokens