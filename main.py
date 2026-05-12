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
