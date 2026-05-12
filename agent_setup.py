import os
import json
from dotenv import load_dotenv
from agents import (
    Agent,
    function_tool,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_default_openai_client,
    set_tracing_disabled
)
from tavily import TavilyClient

# Load environment variables from .env file
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

# Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Using gemini-2.5-flash for the latest performance
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
    # Enhance the query to focus on Quranic verses and Tafsir
    enhanced_query = f"Quranic verses and Tafsir about {query}"
    response = client.search(query=enhanced_query, max_results=5, include_answer="basic")
    return json.dumps(response)

agent = Agent(
    name="IslamicGuidanceAgent",
    instructions=(
        "You are a knowledgeable and empathetic Islamic guidance assistant. "
        "Your goal is to provide guidance based on the Quran for any user question or concern.\n\n"
        "Follow these steps:\n"
        "1. Use the `search_quran` tool to find relevant verses (ayah) related to the user's query.\n"
        "2. Identify at least 2 relevant verses.\n"
        "3. Provide the output in the following format for EACH verse:\n"
        "   - **Arabic Verse:** (The original Arabic text)\n"
        "   - **Translation:** (A clear English translation, e.g., Sahih International or Clear Quran)\n"
        "   - **Tafsir:** (A brief, authentic interpretation/context in English)\n"
        "4. Conclude with a short, encouraging summary or advice based on the verses provided.\n\n"
        "Constraints:\n"
        "- Use ONLY Quranic text and authentic Tafsir.\n"
        "- Ensure the Arabic text is accurate.\n"
        "- Be respectful and professional in your tone."
    ),
    tools=[search_quran],
    model=model
)
