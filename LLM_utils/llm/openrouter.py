import os
from typing import List

from .base_llm import BaseLLM
import requests
import json
import tiktoken
import openai
from openai import OpenAI


class OpenRouter_Deepseek_R1(BaseLLM):
    """Class for the Deepseek-R1 model from Hub with 4000 tokens of context"""

    def __init__(self):
        """Constructor for the Deepseek-R1 class
        Args:
            prompt_token_cost (float): Cost of a token in the prompt
            response_token_cost (float): Cost of a token in the response
        """
        super().__init__(0.0005 / 1000, 0.0015 / 1000, 32000, 0.7)

        self.logger.debug("Loading Deepseek-R1 model from HUB API...")
        # Load the Deepseek-R1 model
        self.client = OpenAI(
            base_url=os.getenv("OPENROUTER_URL"),
            api_key=os.getenv("OPENROUTER_KEY"),
        )
        self.deployment_name = "Deepseek/Deepseek-r1"
        # Encoding to estimate the number of tokens
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0125")

        self.logger.debug("Hub Deepseek-R1 model loaded")

    def _format_prompt(self, prompt: str, role: str = 'user') -> list[dict[str, str]]:
        """Format the prompt to be used by the Deepseek-R1 model
        Args:
            prompt (str): Prompt
        Returns:
            list: List of dictionaries containing the prompt and the role of the speaker
        """
        return [
            {"content": prompt, "role": role}
        ]

    def __completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Completion api for the Deepseek-R1 model
        Args:
            prompt (str): Prompt for the completion
        Returns:
            tuple(str, int, int): A tuple with the completed text, the number of tokens in the prompt and the number of tokens in the response
        """
        prompt = self._format_prompt(prompt)

        # Check if there is a system prompt
        if "system_prompt" in kwargs:
            system_prompt = self._format_prompt(kwargs["system_prompt"], role="system")
            prompt = system_prompt + prompt
            del kwargs["system_prompt"]

        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=prompt,
            extra_body={
                "provider": {
                    "only": ["DeepInfra"],
                    "allow_fallbacks": False
                }
            },
            **kwargs
        )
        completion = response.choices[0].message.content
        prompt_tokens = response.usage.prompt_tokens
        response_tokens = response.usage.completion_tokens

        return completion, prompt_tokens, response_tokens

    def _completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Wrapper for the completion api with retry and exponential backoff

        Args:
            prompt (str): Prompt for the completion

        Returns:
            tuple(str, int, int): A tuple with the completed text, the number of tokens in the prompt and the number of tokens in the response
        """
        wrapper = BaseLLM.retry_with_exponential_backoff(self.__completion, self.logger, errors=(Exception,))
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



class OpenRouter_O4_Mini(BaseLLM):
    """Class for the O4_Mini model from Hub with 4000 tokens of context"""

    def __init__(self):
        """Constructor for the O4_Mini class
        Args:
            prompt_token_cost (float): Cost of a token in the prompt
            response_token_cost (float): Cost of a token in the response
        """
        super().__init__(0.0005 / 1000, 0.0015 / 1000, 32000, 0.7)

        self.logger.debug("Loading O4_Mini model from HUB API...")
        # Load the O4_Mini model
        self.client = OpenAI(
            base_url=os.getenv("OPENROUTER_URL"),
            api_key=os.getenv("OPENROUTER_KEY"),
        )
        self.deployment_name = "openai/o4-mini"
        # Encoding to estimate the number of tokens
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0125")

        self.logger.debug("Hub O4_Mini model loaded")

    def _format_prompt(self, prompt: str, role: str = 'user') -> list[dict[str, str]]:
        """Format the prompt to be used by the O4_Mini1 model
        Args:
            prompt (str): Prompt
        Returns:
            list: List of dictionaries containing the prompt and the role of the speaker
        """
        return [
            {"content": prompt, "role": role}
        ]

    def __completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Completion api for the O4_Mini model
        Args:
            prompt (str): Prompt for the completion
        Returns:
            tuple(str, int, int): A tuple with the completed text, the number of tokens in the prompt and the number of tokens in the response
        """
        prompt = self._format_prompt(prompt)

        # Check if there is a system prompt
        if "system_prompt" in kwargs:
            system_prompt = self._format_prompt(kwargs["system_prompt"], role="system")
            prompt = system_prompt + prompt
            del kwargs["system_prompt"]

        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=prompt,
            **kwargs
        )
        completion = response.choices[0].message.content
        prompt_tokens = response.usage.prompt_tokens
        response_tokens = response.usage.completion_tokens

        return completion, prompt_tokens, response_tokens

    def _completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Wrapper for the completion api with retry and exponential backoff

        Args:
            prompt (str): Prompt for the completion

        Returns:
            tuple(str, int, int): A tuple with the completed text, the number of tokens in the prompt and the number of tokens in the response
        """
        wrapper = BaseLLM.retry_with_exponential_backoff(self.__completion, self.logger, errors=(Exception,))
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
