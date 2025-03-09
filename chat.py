from typing import Generator
from streamlit.runtime.state import SessionStateProxy

import os
import yaml
from qdrant_client import QdrantClient
from simple_llm.agents.delegator import Delegator, DelegatorClient
from simple_llm.embeddings.openai import openai_embedding
from simple_llm.clients.openai import OpenAIAgent
from dotenv import load_dotenv

load_dotenv()

from agents import Researcher, Advisor, Analyst

with open("model_config.yaml", "r", encoding="utf-8") as file:
    model_config = yaml.safe_load(file)

class Chat:
    def __init__(self, agents: list[OpenAIAgent], delegator: Delegator, session: SessionStateProxy):
        self.agents = agents
        self.delegator = delegator
        self.session = session
        self.last_agent = 0

        for agent in self.agents:
            agent._messages += session.messages

    def reply(self, query: str) -> Generator[str, str, None]:
        self.session.messages.append({"role": "user", "content": query})
        index = int(self.delegator.delegate(query))

        if index == 9:
            index = self.last_agent
        else:
            self.last_agent = index

        # print(f"LAST AGENT: {self.last_agent} / AGENTS: {self.agents}")
        agent = self.agents[self.last_agent]
        # print(f"AGENT MESSAGES: {agent._messages}")

        return agent.stream_reply(query)
    
class StockAdvisorChat(Chat):
    def __init__(self, session: SessionStateProxy):
        agents = [Researcher(), Researcher(), Advisor(), Analyst()]
        vec_client = QdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ["QDRANT_API_KEY"])
        del_client = DelegatorClient(vec_client, "delegator-prompts", openai_embedding)
        delegator = Delegator(agent_cls=OpenAIAgent, delegator_client=del_client, **model_config["delegator"])
        super().__init__(agents, delegator, session)

        