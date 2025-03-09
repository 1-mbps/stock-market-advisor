from simple_llm.agents.delegator import DelegatorClient
from simple_llm.embeddings.openai import openai_embedding

from qdrant_client import QdrantClient, models
import dotenv
import os

dotenv.load_dotenv()

client = QdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ["QDRANT_API_KEY"])

client.create_collection(
    collection_name="delegator-prompts",
    vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
)

db = DelegatorClient(client, "delegator-prompts", openai_embedding)

prompts = {
    "1": [
        "Tell me more about the state of the tech industry",
        "Tell me about the latest trends in the fashion industry",
        "What does [company] produce?",
        "Tell me about [company]'s finances",
        "What is [company]?",
        "What's the current price of [stock]?",
        "Is [company] currently involved in any scandals?"
    ],
    "2": [
        "Is [stock] a good buy?",
        "Should I sell [stock]?",
        "Is [company] in a favorable position right now?",
        "Does [company] have a moat?",
        "Is [company] a monopoly?",
        "Do you think [stock] will go up?",
        "Why is [stock] going up right now?"
    ],
    "3": [
        "What are analysts saying about [stock]?",
        "What do users on Reddit think about [company]?",
        "What do people think about [company]'s products?",
        "Do analysts think [stock] is overvalued?",
        "Are people pessimistic about [industry]?",
        "How do traders feel about [company]'s earnings report?",
        "Is there hype around [stock] right now?"
    ],
    "9": [
        "Tell me more about [topic]",
        "Tell me more about [stock]",
        "Expand on that last point",
        "Can you rephrase the first paragraph?",
        "Give me more info"
    ]
}

prompt_list = []
categories = []

for cat, p_list in prompts.items():
    prompt_list += p_list
    categories += [cat]*len(p_list)

# print(prompt_list)
# print(categories)
# print(len(prompt_list))
# print(len(categories))

db.build_collection(prompt_list, categories)
