import praw
import os
import dotenv
from typing import Annotated
from simple_llm.tools.models import Tool
import yaml

from perplexity_agent import PerplexityAgent

dotenv.load_dotenv()

with open("model_config.yaml", "r", encoding="utf-8") as file:
    model_config = yaml.safe_load(file)

credentials = {
    'client_id': os.environ["REDDIT_CLIENT_ID"],
    'client_secret': os.environ["REDDIT_CLIENT_SECRET"],
    'user_agent': os.environ["REDDIT_USER_AGENT"],
    'redirect_uri': "http://localhost:8080"
}

def stock_reddit_search(
    stock_ticker: Annotated[str, "The ticker of the stock the user mentioned."],
    subreddit: Annotated[str, "Only change this if the user wants you to search a specific subreddit."] = "valueinvesting",
    time_filter: Annotated[str, "Only change this if the user wants you to limit your search to a specific time range."] = "year"
) -> str:
    return reddit_search(stock_ticker, subreddit, time_filter)

def search_reddit(
    search_query: Annotated[str, "Describe the topic or area the user needs information on, in 5 words or less."],
    subreddit: Annotated[str, "You may change this subreddit if you think the subreddit mentioned in the default value is not appropriate, or if the user asks you to change it."] = "stocks",
    time_filter: Annotated[str, "Only change this if the user wants you to limit your search to a specific time range."] = "year"
) -> str:
    return reddit_search(search_query, subreddit, time_filter)

def perplexity_search(
    search_query: Annotated[str, "Describe any information required to answer the user's query in 10 words or less."]
) -> str:
    agent = PerplexityAgent(name="researcher", **model_config["researcher"])
    return agent.nostream_reply(search_query)
    
def reddit_search(search_query: str, subreddit: str, time_filter: str) -> str:
    """
    Searches a subreddit.

    Returns:
    - list: A list of dictionaries containing post details (title, author, score, url, content).
    """
    # Initialize Reddit instance
    reddit = praw.Reddit(**credentials)

    # Search subreddit
    subreddit = reddit.subreddit(subreddit)
    submissions = subreddit.search(search_query, limit=5, time_filter=time_filter)  # Adjust limit as needed

    # Collect results
    results = []
    for submission in submissions:
        post_data = {
            'title': submission.title,
            'url': submission.url,
            'content': submission.selftext,
            'comments': []
        }

        if not submission.selftext:
            continue

        # Get top comments and replies
        submission.comment_sort = 'top'  # Sort comments by best
        submission.comments.replace_more(limit=1)  # Load more comments (1 layer deep)
        
        # Collect top 10 comments
        for comment in submission.comments[:5]:
            if isinstance(comment, praw.models.MoreComments) or comment.score <= 0:
                # Skip "load more comments" placeholders and comments with non-positive scores
                continue

            comment_data = {
                'body': comment.body,
                # 'author': str(comment.author) if comment.author else '[deleted]',
                # 'score': comment.score,
                'replies': []
            }

            # Get top 3 replies for each comment
            comment.replies.replace_more(limit=0)  # Don't load deeper replies
            for reply in comment.replies[:3]:
                if reply.score > 0:
                    reply_data = {
                        'body': reply.body,
                        'author': str(reply.author) if reply.author else '[deleted]',
                        'score': reply.score
                    }
                    comment_data['replies'].append(reply_data)

            post_data['comments'].append(comment_data)
        
        results.append(post_data)

        result_str = ""
        for post in results:
            result_str += f"\nPost Title: {post['title']}\nURL: {post['url']}\nText: {post['content']}\n"
            for i, comment in enumerate(post['comments'], 1):
                result_str += f"\nComment {i}: {comment['body']}"
                for j, reply in enumerate(comment['replies'], 1):
                    result_str += f"\nReply {j} to Comment {i}: {reply['body']}"

        return result_str

StockRedditSearch = Tool(
    name="stock_reddit_search",
    description="Use this tool to search Reddit for detailed information and crowdsourced analysis about a particular stock.",
    function=stock_reddit_search
)

RedditSearch = Tool(
    name="general_reddit_search",
    description="Use this tool to search Reddit for detailed information and crowdsourced analysis about a particular topic.",
    function=search_reddit
)

PerplexitySearch = Tool(
    name="research_tool",
    description="Use this tool to perform research on a particular topic.",
    function=perplexity_search
)