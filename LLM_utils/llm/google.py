import os
import google.generativeai as genai
from typing import List

from PIL.Image import Image
from statannotations.stats.ComparisonsCorrection import IMPLEMENTED_METHODS

from .base_llm import BaseLLM
import tiktoken
import PIL.Image


class Gemini(BaseLLM):
    """Class for the Gemini model from Google with 8.000 tokens of context"""

    def __init__(self):
        """Constructor for the GeminiVision class
        Args:
            prompt_token_cost (float): Cost of a token in the prompt
            response_token_cost (float): Cost of a token in the response
        """
        # https://ai.google.dev/gemini-api/docs
        # https://ai.google.dev/pricing
        super().__init__(1.25/1000000, 5/1000000, 128000, 0.7)

        self.logger.debug("Loading GeminiPro model from the GOOGLE API...")
        # Load the model
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

        self.client = genai.GenerativeModel(model_name=os.getenv('GOOGLE_GEMINI_MODEL_ID'))

        self.deployment_name = os.getenv("GOOGLE_GEMINI_MODEL_ID")
        self.logger.debug("Deployment name: " + self.deployment_name)
        # Encoding to estimate the number of tokens
        self.encoding = tiktoken.encoding_for_model("gpt-4-turbo")

        self.logger.debug("GeminiPro model loaded")

    def _format_prompt(self, prompt: str) -> list[str]:
        """Format the prompt to be used by the Gemini model
        Args:
            prompt (str): Prompt
        Returns:
            List: List of dictionaries containing the prompt and the role of the speaker
        """
        return [prompt]

    def __completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Completion api for the Gemini model
        Args:
            prompt (str): Prompt for the completion
        Returns:
            tuple(str, int, int): A tuple with the completed text, the number of tokens in the prompt and the number of tokens in the response
        """

        prompt = self._format_prompt(prompt)

        # Check that the prompt is not too long
        if self._calculate_tokens(prompt) > self.max_tokens * self.max_tokens_ratio_per_input:
            raise ValueError("Prompt is too long")
        # Check if there is a system prompt
        if "system_prompt" in kwargs:
            system_prompt = kwargs["system_prompt"]
            del kwargs["system_prompt"]
            self.client = genai.GenerativeModel(model_name=os.getenv('GOOGLE_GEMINI_MODEL_ID'), system_instruction=system_prompt)

        if "temperature" in kwargs:
            temperature = kwargs["temperature"]


            response = self.client.generate_content(prompt, stream=True,
                generation_config = genai.GenerationConfig(
                temperature=temperature,
            ))
        else:
            response = self.client.generate_content(prompt, stream=True)
        response.resolve()
        completion = response.text
        prompt_tokens = self.client.count_tokens(prompt).total_tokens
        response_tokens = self.client.count_tokens(completion).total_tokens

        return completion, prompt_tokens, response_tokens

    def _completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Wrapper for the completion api with retry and exponential backoff

        Args:
            prompt (str): Prompt for the completion

        Returns:
            tuple(str, int, int): A tuple with the completed text, the number of tokens in the prompt and the number of tokens in the response
        """
        wrapper = BaseLLM.retry_with_exponential_backoff(self.__completion, self.logger, errors=(
            genai.types.IncompleteIterationError, genai.types.BrokenResponseError))
        return wrapper(prompt, **kwargs)

    def _calculate_tokens(self, prompt: str) -> int:
        """Calculate the number of tokens in the prompt
        Args:
            prompt (str): Prompt
        Returns:
            int: Number of tokens in the prompt
        """
        num_tokens = self.client.count_tokens(prompt).total_tokens 
        return num_tokens

    def completion(self, prompt: str, **kwargs) -> str:
        """Method for the completion api. It updates the cost of the prompt and response and log the tokens and prompts
        Args:
            prompt (str): Prompt file or string for the completion
            inputs (list[str]): List of inputs to replace the <input{number}> in the prompt. For example: ["This is the first input", "This is the second input"]
        Returns:
            str: Completed text
        """

        prompt = self._load_prompt(prompt)
        prompt = self._replace_inputs_in_prompt(prompt, kwargs.get("inputs", []))

        self.logger.debug(f"Prompt: {prompt}")
        kwargs.pop("inputs", None)  # Remove the inputs from the kwargs to avoid passing them to the completion api
        response, prompt_tokens, response_tokens = self._completion(prompt, **kwargs)
        self.logger.debug(f"Response: {response}")

        self._update_costs(prompt_tokens, response_tokens)
        self.logger.debug(f"Prompt tokens: {prompt_tokens}")
        self.logger.debug(f"Response tokens: {response_tokens}")

        return response


if __name__ == '__main__':
    from dotenv import load_dotenv

    load_dotenv(override=True)

    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)

    print(GOOGLE_API_KEY)

    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)

    model = genai.GenerativeModel(os.getenv('GOOGLE_GEMINI_MODEL_ID'))

