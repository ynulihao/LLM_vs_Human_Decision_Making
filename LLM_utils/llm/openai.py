import os
from typing import List

from .base_llm import BaseLLM
import openai
from openai import OpenAI
import tiktoken



class GPT4(BaseLLM):
    """Class for the GPT-4 model from OpenAI with 8.000 tokens of context"""

    def __init__(self):
        """Constructor for the GPT4 class
        Args:
            prompt_token_cost (float): Cost of a token in the prompt
            response_token_cost (float): Cost of a token in the response
        """
        super().__init__(0.01 / 1000, 0.03 / 1000, 128000, 0.7)

        self.logger.debug("Loading GPT-4 model from the OPENAI API...")
        # Load the model
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.deployment_name = os.getenv("OPENAI_GPT_4_MODEL_ID")
        self.logger.debug("Deployment name: " + self.deployment_name)
        # Encoding to estimate the number of tokens
        self.encoding = tiktoken.encoding_for_model("gpt-4-turbo-preview")

        self.logger.debug("GPT-4 model loaded")

    def _format_prompt(self, prompt: str, role: str = 'user') -> list[dict[str, str]]:
        """Format the prompt to be used by the GPT-4 model
        Args:
            prompt (str): Prompt
        Returns:
            list: List of dictionaries containing the prompt and the role of the speaker
        """
        return [
            {"content": prompt, "role": role}
        ]

    def __completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Completion api for the GPT-4 model
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


class GPT4O(GPT4):
    """Class for the GPT-4O model from OpenAI with 8.000 tokens of context"""

    def __init__(self):
        """Constructor for the GPT4O class
        Args:
            prompt_token_cost (float): Cost of a token in the prompt
            response_token_cost (float): Cost of a token in the response
        """
        BaseLLM.__init__(self, 0.00015 / 1000, 0.0006 / 1000, 128000, 0.7)

        self.logger.debug("Loading GPT-4O model from the OPENAI API...")
        # Load the model
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.deployment_name = os.getenv("OPENAI_GPT_4O_MODEL_ID")
        self.logger.debug("Deployment name: " + self.deployment_name)
        # Encoding to estimate the number of tokens
        self.encoding = tiktoken.encoding_for_model("gpt-4-turbo-preview")

        self.logger.debug("GPT-4O model loaded")


class Ada(BaseLLM):
    """Class for the Ada model from OpenAI"""

    def __init__(self):
        """Constructor for the Ada class
        Args:
            prompt_token_cost (float): Cost of a token in the prompt
            response_token_cost (float): Cost of a token in the response
        """
        super().__init__(0.0001 / 1000, 0, 8191, 1)

        self.logger.debug("Loading Ada model...")
        # Load the Ada model
        self.client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.deployment_name = os.getenv("OPENAI_TEXT_EMBEDDING_MODEL_ID")
        # Encoding to estimate the number of tokens
        self.encoding = tiktoken.encoding_for_model("text-embedding-ada-002")
        # Embedding dimensions
        self.embedding_dimensions = 1536

        self.logger.debug("Ada model loaded")

    def __embed(self, text: str, **kwargs) -> tuple[list[float], int, int]:
        """Embedding api for the Ada model
        Args:
            text (str): Text to embed
        Returns:
            tuple(list[float], int, int): A tuple with the embedded text, the number of tokens in the prompt and the number of tokens in the response
        """
        # response = get_embedding(text, engine=self.deployment_name, **kwargs)
        response = self.client.embeddings.create(input=[text], model=self.deployment_name)

        embedding = response.data[0].embedding
        prompt_tokens = response.usage.total_tokens
        response_tokens = 0

        return embedding, prompt_tokens, response_tokens

    def _completion(self, text: str, **kwargs) -> tuple[list[float], int, int]:
        """Wrapper for the completion api with retry and exponential backoff

        Args:
            text (str): Text to embed

        Returns:
            tuple(list[float], int, int): A tuple with the embedded text, the number of tokens in the prompt and the number of tokens in the response
        """
        wrapper = BaseLLM.retry_with_exponential_backoff(self.__embed, self.logger, errors=(
            openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError))
        return wrapper(text, **kwargs)

    def _calculate_tokens(self, text: str) -> int:
        """Calculate the number of tokens in the text
        Args:
            text (str): Text to embed
        Returns:
            int: Number of tokens in the text
        """
        num_tokens = len(self.encoding.encode(text))
        return num_tokens

    def get_embedding(self, text: str) -> list[float]:
        """Get the embedding of a text
        Args:
            text (str): Text to embed
        Returns:
            list[float]: Embedding of the text
        """

        # Check that the prompt is not too long
        tokens = self._calculate_tokens(text)
        if tokens > self.max_tokens * self.max_tokens_ratio_per_input:
            raise ValueError("Text is too long to embed")

        embedding, prompt_tokens, response_tokens = self._completion(text)

        # Update the cost of the prompt and response
        self._update_costs(prompt_tokens, response_tokens)
        return embedding

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Get the embeddings of a list of texts
        Args:
            texts (list[str]): List of texts to embed
        Returns:
            list[list[float]]: List of embeddings of the texts
        """
        embeddings = []
        for text in texts:
            embeddings.append(self.get_embedding(text))
        return embeddings

