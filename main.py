# main.py

import chainlit as cl
from agent_setup import agent
from agents import Runner



# agent_setup.py

from agents import Agent, function_tool
from tavily import TavilyClient
import os
import json
from pydantic import BaseModel
from agents import (
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunConfig
)
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

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)
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
        "find and quote relevant Quranic 2 or more than 2 verses (ayah) **in Arabic**, provide their English translation, "
        "and include a brief Tafsir (interpretation) in English. "
        "Use the `search_quran` tool to find verses that address the user’s query. "
        "Format the answer clearly with labeled sections:\n"
        "- **Arabic Verse:** <Arabic text>\n"
        "- **Translation:** <English translation>\n"
        "- **Tafsir:** <English commentary>\n"
        "Use only Quranic text and authentic Tafsir in your response."
        "provide 2 or more than 2 verses and their translation"

    ),
    tools=[search_quran],
    model=model
)




# main.py

import chainlit as cl
from agent_setup import agent
from agents import Runner

MAX_MEMORY = 5  # number of past Q&A to remember in short-term memory

@cl.on_chat_start
async def start():
    # Initialize session memory
    cl.user_session.set("memory", [])
    await cl.Message(content="🤲 **Welcome to the Islamic Guidance Assistant!**\nAsk a question to receive guidance from the Quran.").send()

@cl.on_message
async def handle_message(message: cl.Message):
    query = message.content

    # Retrieve current memory
    memory = cl.user_session.get("memory", [])

    # Add the new query to context
    context_prompt = ""
    if memory:
        context_prompt += "Previous questions and answers:\n"
        for i, (q, a) in enumerate(memory[-MAX_MEMORY:], 1):
            context_prompt += f"\nQ{i}: {q}\nA{i}: {a}\n"

    # Combine context and current query
    contextual_query = context_prompt + f"\nNow answer this: {query}"

    # Let user know it’s working
    await cl.Message(content="🔍 Searching the Quran with context...").send()

    # Run the OpenAI Agent
    result = await Runner.run(agent, input=contextual_query)

    # Send response
    await cl.Message(content=result.final_output).send()

    # Update memory with the new Q&A
    memory.append((query, result.final_output))
    cl.user_session.set("memory", memory)




# @cl.on_chat_start
# async def start():
#     await cl.Message(content="🤲 **Welcome to the Islamic Guidance Assistant!**\nAsk a question to receive guidance from the Quran.").send()

# @cl.on_message
# async def handle_message(message: cl.Message):
#     query = message.content
#     await cl.Message(content="🔍 Searching for relevant Quranic guidance...").send()

#     # Run the OpenAI Agent
#     result = await Runner.run(agent, input=query, run_config=config)

#     # Send formatted response
#     await cl.Message(content=result.final_output).send()
