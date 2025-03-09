from simple_llm.clients.openai import BaseOpenAIAgent
from openai import OpenAI
import os

class PerplexityAgent(BaseOpenAIAgent):
    def __init__(self, name: str, model: str, system_message: str, stream: bool = False, track_msgs: bool = True, track_usage: bool = True, tools: list = [], default_params: dict = {}, api_key = None):
        client = OpenAI(base_url="https://api.perplexity.ai", api_key=api_key or os.getenv("PERPLEXITY_API_KEY"))
        super().__init__(name, model, client, system_message, stream, track_msgs, track_usage, tools, default_params, api_key, api_type="perplexity")