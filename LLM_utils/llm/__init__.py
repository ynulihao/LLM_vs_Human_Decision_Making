from .base_llm import BaseLLM
from .openai import Ada, GPT4, GPT4O
from .google import Gemini
from .claude import CLAUDE_3_5_SONNET
from .hub import HUB_CLAUDE_3_5_SONNET, HUB_Gemini, HUB_Deepseek_R1, HUB_O4_MINI
from .openrouter import OpenRouter_Deepseek_R1, OpenRouter_O4_Mini

class LLMModels():
    """Class to define the available LLM models"""

    def __new__(self):
        """Constructor for the LLMModels class"""
        # Singleton pattern
        if not hasattr(self, 'instance'):
            self.instance = super(LLMModels, self).__new__(self)
            self.instance.llm_models: dict[str, BaseLLM] = {

            "gpt-4o": GPT4O(),
            "gemini-1.5-pro": Gemini(),
            "claude-3-5-sonnet": CLAUDE_3_5_SONNET(),

            "hub-claude-3-5-sonnet": HUB_CLAUDE_3_5_SONNET(),
            "hub-gemini-1.5-pro": HUB_Gemini(),
            "hub-Deepseek-r1": HUB_Deepseek_R1(),
            "hub-o4-mini": HUB_O4_MINI(),
            
            "openrouter-Deepseek-r1": OpenRouter_Deepseek_R1(),
            "openrouter-o4-mini": OpenRouter_O4_Mini(),
            "ada": Ada()
            }
            self.instance.gpt_4o_model = "gpt-4o"
            self.instance.gemini_pro_1_5_model = "gemini-1.5-pro"
            self.instance.claude_3_5_sonnet_model = "claude-3-5-sonnet"
            
            self.instance.hub_claude_3_5_sonnet_model = "hub-claude-3-5-sonnet"
            self.instance.hub_gemini_1_5_pro_model = "hub-gemini-1.5-pro"
            self.instance.hub_Deepseek_r1_model = "hub-Deepseek-r1"
            self.instance.hub_o4_mini_model = "hub-o4-mini"
            
            self.instance.openrouter_Deepseek_r1_model = "openrouter-Deepseek-r1"
            self.instance.openrouter_o4_mini_model = "openrouter-o4-mini"
    
            self.instance.embedding_model = "ada"


        return self.instance


    def get_gpt_4o_model(self) -> BaseLLM:
        """Get the gpt-4o model
        Returns:
            BaseLLM: GPT4O model
        """
        return self.llm_models[self.gpt_4o_model]

    def get_gemini_1_5_pro_model(self) -> BaseLLM:
        """Get the gemini-1.5-pro model
        Returns:
            BaseLLM: gemini model
        """
        return self.llm_models[self.gemini_pro_1_5_model]

    def get_claude_3_5_sonnet_model(self) -> BaseLLM:
        """Get the claude-3-5-sonnet model
        Returns:
            BaseLLM: claude-3-5-sonnet model
        """
        return self.llm_models[self.claude_3_5_sonnet_model]

    def get_hub_claude_3_5_sonnet_model(self) -> BaseLLM:
        """Get the hub-claude-3-5-sonnet model
        Returns:
            BaseLLM: hub-claude-3-5-sonnet model
        """
        return self.llm_models[self.hub_claude_3_5_sonnet_model]

    def get_hub_gemini_1_5_pro_model(self) -> BaseLLM:
        """Get the hub-gemini-1.5-pro model
        Returns:
            BaseLLM:  hub-gemini-1.5-pro model
        """
        return self.llm_models[self.hub_gemini_1_5_pro_model]

    def get_hub_Deepseek_r1_model(self) -> BaseLLM:
        """Get the hub-Deepseek-r1 model
        Returns:
            BaseLLM:  hub-Deepseek-r1 model
        """
        return self.llm_models[self.hub_Deepseek_r1_model]
    
    def get_hub_o4_mini_model(self) -> BaseLLM:
        """Get the hub-o4-mini model
        Returns:
            BaseLLM:  hub-o4-mini model
        """
        return self.llm_models[self.hub_o4_mini_model]
    
    def get_openrouter_Deepseek_r1_model(self) -> BaseLLM:
        """Get the openrouter-Deepseek-r1 model

        Returns:
            BaseLLM: openrouter-Deepseek-r1 model
        """
        return self.llm_models[self.openrouter_Deepseek_r1_model]
    
    def get_openrouter_o4_mini_model(self) -> BaseLLM:
        """Get the openrouter-o4-mini model
        Returns:
            BaseLLM: openrouter-o4-mini model
        """
        return self.llm_models[self.openrouter_o4_mini_model]

    def get_embedding_model(self) -> BaseLLM:
        """Get the embedding model
        Returns:
            BaseLLM: Embedding model
        """
        return self.llm_models[self.embedding_model]

        return self.llm_models[self.intern_2_5]

    def get_costs(self) -> dict:
        """Get the costs of the models
        Returns:
            dict: Costs of the models
        """
        costs = {}
        total_cost = 0
        for model_name, model in self.llm_models.items():
            model_cost = model.cost_manager.get_costs()['total_cost']
            costs[model_name] = model_cost
            total_cost += model_cost

        costs['total'] = total_cost

        return costs

    def get_tokens(self) -> dict:
        """Get the tokens used by the models
        Returns:
            dict: Tokens used by model
        """
        tokens = {}
        total_tokens = 0
        for model_name, model in self.llm_models.items():
            model_tokens = model.cost_manager.get_tokens()['total_tokens']
            tokens[model_name] = model_tokens
            total_tokens += model_tokens

        tokens['total'] = total_tokens

        return tokens
