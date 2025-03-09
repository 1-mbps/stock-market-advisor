from simple_llm.clients.openai import OpenAIAgent
from perplexity_agent import PerplexityAgent
import yaml

from tools import StockRedditSearch, RedditSearch, PerplexitySearch

with open("model_config.yaml", "r", encoding="utf-8") as file:
    model_config = yaml.safe_load(file)

class Researcher(PerplexityAgent):
    def __init__(self):
        super().__init__(name="researcher", **model_config["researcher"])

class Advisor(OpenAIAgent):
    def __init__(self):
        super().__init__(name="advisor", **model_config["advisor"], tools=[StockRedditSearch, PerplexitySearch])

class Analyst(OpenAIAgent):
    def __init__(self):
        super().__init__(name="researcher", **model_config["analyst"], tools=[StockRedditSearch, RedditSearch])