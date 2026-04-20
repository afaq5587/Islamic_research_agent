

# agent_setup.py

from agents import Agent, function_tool
from tavily import TavilyClient
import os
import json
from pydantic import BaseModel
from dotenv import load_dotenv
from agents import (
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunConfig
)

# Load environment variables from .env file
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

from agents import set_default_openai_client, set_tracing_disabled


# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

#Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)
set_default_openai_client(external_client)
set_tracing_disabled(True)

@function_tool
def search_quran(query: str) -> str:
    """
    Search for Quranic verses related to the query using the Tavily API.
    Returns raw JSON string of the search results.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is not set.")
    client = TavilyClient(api_key=api_key)
    response = client.search(query=query, max_results=5, include_answer="basic")
    return json.dumps(response)

agent = Agent(
    name="IslamicGuidanceAgent",
    instructions=(
        "You are an Islamic guidance assistant. For any user question or concern, "
        "find and quote relevant Quranic verses (ayah) **in Arabic**, provide their English translation, "
        "and include a brief Tafsir (interpretation) in English. "
        "Use the `search_quran` tool to find verses that address the user’s query. "
        "Format the answer clearly with labeled sections:\n"
        "- **Arabic Verse:** <Arabic text>\n"
        "- **Translation:** <English translation>\n"
        "- **Tafsir:** <English commentary>\n"
        "Use only Quranic text and authentic Tafsir in your response."
    ),
    tools=[search_quran],
    model=model
)


