from .base_llm import MockLLM
from collections import defaultdict

class LLMModels():
    """Class to define the available LLM models"""

    def __new__(self):
        """Constructor for the LLMModels class"""
        # Singleton pattern
        if not hasattr(self, 'instance'):
            self.instance = super(LLMModels, self).__new__(self)
            self.instance.llm_models: dict[str, MockLLM] = defaultdict(lambda: MockLLM())
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
 

    def get_gpt_4o_model(self) -> MockLLM:
        """Get the gpt-4o model
        Returns:
            MockLLM: GPT4O model
        """
        return self.llm_models[self.gpt_4o_model]

    def get_gemini_1_5_pro_model(self) -> MockLLM:
        """Get the gemini-1.5-pro model
        Returns:
            MockLLM: Gemini-1.5-pro model
        """
        return self.llm_models[self.gemini_1_5_pro_model]
    
    def get_claude_3_5_sonnet_model(self) -> MockLLM:
        """Get the claude-3-5-sonnet model
        Returns:
            MockLLM: claude-3-5-sonnet model
        """
        return self.llm_models[self.claude_3_5_sonnet_model]
    
    def get_hub_claude_3_5_sonnet_model(self) -> MockLLM:
        """Get the hub-claude-3-5-sonnet model
        Returns:
            MockLLM: hub-claude-3-5-sonnet model
        """
        return self.llm_models[self.hub_claude_3_5_sonnet_model]
    
    def get_hub_gemini_1_5_pro_model(self) -> MockLLM:
        """Get the hub-gemini-1.5-pro model
        Returns:
            MockLLM: hub-gemini-1.5-pro model
        """
        return self.llm_models[self.hub_gemini_1_5_pro_model]   
    
    def get_hub_Deepseek_r1_model(self) -> MockLLM:
        """Get the hub-Deepseek-r1 model
        Returns:
            MockLLM: hub-Deepseek-r1 model
        """
        return self.llm_models[self.hub_Deepseek_r1_model]
    
    def get_hub_o4_mini_model(self) -> MockLLM:
        """Get the hub-o4-mini model
        Returns:
            MockLLM: hub-o4-mini model
        """
        return self.llm_models[self.hub_o4_mini_model]
    
    def get_openrouter_Deepseek_r1_model(self) -> MockLLM:
        """Get the openrouter-Deepseek-r1 model
        Returns:
            MockLLM: openrouter-Deepseek-r1 model
        """
        return self.llm_models[self.openrouter_Deepseek_r1_model]
    
    def get_openrouter_o4_mini_model(self) -> MockLLM:
        """Get the openrouter-o4-mini model
        Returns:
            MockLLM: openrouter-o4-mini model
        """
        return self.llm_models[self.openrouter_o4_mini_model]   

    def get_embedding_model(self) -> MockLLM:
        """Get the embedding model
        Returns:
            MockLLM: Embedding model
        """
        return self.llm_models[self.embedding_model]

    def get_costs(self) -> dict:
        """Get the costs of the models
        Returns:
            dict: Costs of the models
        """
        raise NotImplementedError("This method is not implemented in the MockLLM class.")

    def get_tokens(self) -> dict:
        """Get the tokens used by the models
        Returns:
            dict: Tokens used by model
        """
        raise NotImplementedError("This method is not implemented in the MockLLM class.")
