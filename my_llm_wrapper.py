# my_llm_wrapper.py
from typing import List, Optional
from langchain_community.llms import Ollama
from crewai.llm import BaseLLM

class OllamaCrewAIWrapper(BaseLLM):
    def __init__(self, model_name="llama3"):
        self.llm = Ollama(model=model_name)

    def call(self, prompt: str, stop: Optional[List[str]] = None, callbacks=None) -> str:
        # Ignore stop and callbacks for now, unless you want to use them
        return self.llm.invoke(prompt)
