import os
from typing import List

from .base_llm import BaseLLM
import requests
import json
import tiktoken
import openai
from openai import OpenAI

class HUB_CLAUDE_3_5_SONNET(BaseLLM):
    """Class for the GPT-3.5 turbo model from Hub with 4000 tokens of context"""

    def __init__(self):
        """Constructor for the CLAUDE_3_5_SONNET class
        Args:
            prompt_token_cost (float): Cost of a token in the prompt
            response_token_cost (float): Cost of a token in the response
        """
        super().__init__(0.0003 / 1000, 0.0015 / 1000, 128000, 0.7)

        self.logger.debug("Loading claude-3-5-sonnet model from Hub API...")
        # Load the GPT-3.5 model
        self.client = requests.request
        self.deployment_name = os.getenv("CLAUDE_3_5_SONNET_MODEL_ID")
        # Encoding to estimate the number of tokens
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0125")

        self.logger.debug("claude-3-5-sonnet model loaded")

    def _format_prompt(self, prompt: str, role: str = 'user') -> list[dict[str, str]]:
        """Format the prompt to be used by the CLAUDE_3_5_SONNET model
        Args:
            prompt (str): Prompt
        Returns:
            list: List of dictionaries containing the prompt and the role of the speaker
        """
        return [
            {"content": prompt, "role": role}
        ]

    def __completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Completion api for the CLAUDE_3_5_SONNET model
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

        payload = json.dumps({
            "model": self.deployment_name,  # claude-3-5-sonnet-20241022, gemini-1.5-pro
            "messages": prompt
        })

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {os.getenv("HUB_API_KEY")}',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }

        response = None
        try:
            response = requests.request("POST", os.getenv("HUB_URL"), headers=headers, data=payload).json()
            completion = response['choices'][0]['message']['content']
            if response["usage"] is not None:
                prompt_tokens = response["usage"]["prompt_tokens"]
                response_tokens = response["usage"]["completion_tokens"]
            else:
                prompt_tokens = 0
                response_tokens = 0

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
            requests.HTTPError, requests.ConnectionError, requests.Timeout, KeyError))
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


class HUB_Gemini(BaseLLM):
    """Class for the Gemini model from Google with 8.000 tokens of context"""

    def __init__(self):
        """Constructor for the GeminiVision class
        Args:
            prompt_token_cost (float): Cost of a token in the prompt
            response_token_cost (float): Cost of a token in the response
        """
        super().__init__(1.25/1000000, 5/1000000, 128000, 0.7)

        self.logger.debug("Loading GeminiPro model from the HUB API...")
        # Load the model
        self.client = requests.request
        self.deployment_name = os.getenv("GOOGLE_GEMINI_MODEL_ID")
        # Encoding to estimate the number of tokens
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0125")

        self.logger.debug("claude-3-5-sonnet model loaded")

    def _format_prompt(self, prompt: str, role: str = 'user') -> list[dict[str, str]]:
        """Format the prompt to be used by the Gemini model
        Args:
            prompt (str): Prompt
        Returns:
            list: List of dictionaries containing the prompt and the role of the speaker
        """
        return [
            {"content": prompt, "role": role}
        ]

    def __completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Completion api for the Gemini model
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

        payload = json.dumps({
            "model": self.deployment_name,
            "messages": prompt
        })

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {os.getenv("HUB_API_KEY")}',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }

        response = None
        try:
            response = requests.request("POST", os.getenv("HUB_URL"), headers=headers, data=payload).json()

            completion = response['choices'][0]['message']['content']
            prompt_tokens = response["usage"]["prompt_tokens"]
            response_tokens = response["usage"]["completion_tokens"]
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
            requests.HTTPError, requests.ConnectionError, requests.Timeout, KeyError))
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


class HUB_Deepseek_R1(BaseLLM):
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
            base_url=os.getenv("HUB_URL"),
            api_key=os.getenv("HUB_API_KEY"),
        )
        self.deployment_name = "Deepseek-ai/Deepseek-R1"
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

        response = self.client.chat.completions.create(model=self.deployment_name, messages=prompt, **kwargs)
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
        wrapper = BaseLLM.retry_with_exponential_backoff(self.__completion, self.logger, errors=(
            openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError))
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


class HUB_O4_MINI(BaseLLM):
    """Class for the HUB_O4_MINI model from Hub with 4000 tokens of context"""

    def __init__(self):
        """Constructor for the HUB_O4_MINI class
        Args:
            prompt_token_cost (float): Cost of a token in the prompt
            response_token_cost (float): Cost of a token in the response
        """
        super().__init__(0, 0, 32000, 0.7)

        self.logger.debug("Loading HUB_O4_MINI model from HUB API...")
        # Load the Deepseek-R1 model
        self.client = OpenAI(
            base_url=os.getenv("HUB_URL"),
            api_key=os.getenv("HUB_API_KEY"),
        )
        self.deployment_name = "o4-mini-2025-04-16"
        # Encoding to estimate the number of tokens
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0125")

        self.logger.debug("Hub HUB_O4_MINI model loaded")

    def _format_prompt(self, prompt: str, role: str = 'user') -> list[dict[str, str]]:
        """Format the prompt to be used by the HUB_O4_MINI model
        Args:
            prompt (str): Prompt
        Returns:
            list: List of dictionaries containing the prompt and the role of the speaker
        """
        return [
            {"content": prompt, "role": role}
        ]

    def __completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Completion api for the HUB_O4_MINI model
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

        response = self.client.chat.completions.create(model=self.deployment_name, messages=prompt, **kwargs)
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
        wrapper = BaseLLM.retry_with_exponential_backoff(self.__completion, self.logger, errors=(
            openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError))
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


if __name__ == "__main__":
    pass
