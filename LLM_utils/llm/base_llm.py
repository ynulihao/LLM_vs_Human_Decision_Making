from abc import ABC, abstractmethod
import logging
import os
import time
import random
import re
import traceback

from ..utils.llm_cost import CostManager
from ..utils.logger_utils import create_logger


class BaseLLM(ABC):
    """Base class for all LLM classes. It defines the api to use the LLMs"""

    def __init__(self, prompt_token_cost: float, response_token_cost: float, max_tokens: int, max_tokens_ratio_per_input: float = 0.7):
        """Constructor for the BaseLLM class
        Args:
            prompt_token_cost (float): Cost of a token in the prompt
            response_token_cost (float): Cost of a token in the response
            max_tokens (int): Maximum number of tokens
            max_tokens_ratio_per_input (float): Maximum ratio of tokens per input in the prompt, to avoid the LLM to use all the tokens in the prompt for just the input
        """
        self.cost_manager = CostManager(prompt_token_cost, response_token_cost)
        self.max_tokens = max_tokens
        self.max_tokens_ratio_per_input = max_tokens_ratio_per_input

        self.logger = create_logger(self.__class__.__name__)

    @abstractmethod
    def _calculate_tokens(self, prompt:str) -> int:
        """Abstract method for calculating the number of tokens in the prompt
        Args:
            prompt (str): Prompt
        Returns:
            int: Number of tokens in the prompt
        """
        pass

    
    def _update_costs(self, prompt_tokens: int, response_tokens: int):
        """Update the cost of the prompt and response
        Args:
            prompt_tokens (int): Number of tokens in the prompt
            response_tokens (int): Number of tokens in the response
        Returns:
            tuple(int, int): Tuple containing the tokens number of the prompt and response
        """
        self.cost_manager.update_costs(prompt_tokens, response_tokens)

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
            Exception: Maximum number of retries exceeded
            Exception: Any other exception raised by the function that is not specified in the errors tuple

        Returns:
            function: Function to retry with exponential backoff
        """
    
        def wrapper(*args, **kwargs):
            # Initialize variables
            num_retries = 0
            delay = initial_delay
    
            # Loop until a successful response or max_retries is hit or an exception is raised
            while True:
                try:
                    return func(*args, **kwargs)
    
                # Retry on specific errors
                except errors as e:
                    # Increment retries
                    num_retries += 1
    
                    # Check if max retries has been reached
                    if num_retries > max_retries:
                        logger.error("Max retries exceeded with error: %s\n%s", str(e), traceback.format_exc())
                        raise Exception(f"Maximum number of retries ({max_retries}) exceeded.") from e
                    
                    # Increment the delay
                    delay *= exponential_base * (1 + jitter * random.random())

                    logger.warning(
                        "Error in the function '%s' with type %s: %s. Retrying for the %s time. Waiting %.2f seconds\n",
                        func.__name__, type(e).__name__, str(e), num_retries, delay
                    )
    
                    # Sleep for the delay
                    time.sleep(delay)
    
                # Raise exceptions for any errors not specified
                except Exception as e:
                    raise e
    
        return wrapper
    
    @abstractmethod
    def _completion(self, prompt: str, **kwargs) -> tuple[str, int, int]:
        """Abstract method for the completion api
        Args:
            prompt (str): Prompt for the completion
        Returns:
            tuple(str, int, int): A tuple with the completed text, the number of tokens in the prompt and the number of tokens in the response
        """
        pass

    def _load_prompt(self, prompt: str) -> str:
        """Load the prompt from a file or return the prompt if it is a string
        Args:
            prompt_file (str): Prompt file or string
        Returns:
            str: Prompt
        """
        prompt_file = os.path.join("prompts", prompt)

        # Check if the prompt is a string or a file
        if not os.path.isfile(prompt_file):
            if prompt_file.endswith(".txt"):
                logging.error(f"Prompt file: {prompt_file} not found, using the prompt as a string")
                raise ValueError("Prompt file not found")
            return prompt
        
        with open(prompt_file, "r") as f:
            prompt = f.read()
        return prompt
    
    def _replace_inputs_in_prompt(self, prompt: str, inputs: list[str] = []) -> str:
        """Replace the inputs in the prompt. The inputs are replaced in the order they are passed in the list.
        Args:
            prompt (str): Prompt. For example: "This is a <input1> prompt with <input2> two inputs"
            inputs (list[str]): List of inputs
        Returns:
            str: Prompt with the inputs
        """
        for i, input in enumerate(inputs):
            if input is None:
                input = 'None'
            # Delete the line if the input is empty
            if str(input).strip() == "":
                regex = rf"^\s*{re.escape(f'<input{i+1}>')}[ \t\r\f\v]*\n"
                prompt = re.sub(regex, "", prompt, flags=re.MULTILINE)
   
            prompt = prompt.replace(f"<input{i+1}>", str(input))

        # Check if there are any <input> left
        if "<input" in prompt:
            raise ValueError("Not enough inputs passed to the prompt")
        return prompt

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

        # Check that the prompt is not too long
        if self._calculate_tokens(prompt) > self.max_tokens * self.max_tokens_ratio_per_input:
            raise ValueError("Prompt is too long")
        
        self.logger.debug(f"Prompt: {prompt}")
        kwargs.pop("inputs", None) # Remove the inputs from the kwargs to avoid passing them to the completion api
        response, prompt_tokens, response_tokens = self._completion(prompt, **kwargs)
        self.logger.debug(f"Response: {response}")

        self._update_costs(prompt_tokens, response_tokens)
        self.logger.debug(f"Prompt tokens: {prompt_tokens}")
        self.logger.debug(f"Response tokens: {response_tokens}")

        return response