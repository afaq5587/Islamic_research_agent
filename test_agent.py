import asyncio
from agent_setup import agent
from agents import Runner
import os

async def main():
    print("Testing Islamic Guidance Agent...")
    try:
        # Simple test query
        query = "What does the Quran say about patience (Sabr)?"
        print(f"Query: {query}")
        
        result = await Runner.run(agent, input=query)
        
        print("\n--- Final Output ---")
        print(result.final_output)
        print("--------------------")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
