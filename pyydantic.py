from pydantic import BaseModel
from agents import (
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunConfig,
    function_tool,
    Agent,
    Runner,
    enable_verbose_stdout_logging,
    set_tracing_disabled
)
import os
from dotenv import load_dotenv

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

from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserINfo(BaseModel):

  city: str
  temperature : float
  unit : str = "Celsius"
  description: str
  
import asyncio
import os
import requests
from agents import Agent, Runner, function_tool
# from litellm import completion

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
enable_verbose_stdout_logging()
@function_tool
def get_weather(city: str) -> str:
    """Fetch the current weather for a given city using OpenWeatherMap API.

    Args:
        city: The name of the city to fetch the weather for.
    """
    api_key = OPENWEATHERMAP_API_KEY
    if not api_key:
        return "Error: OpenWeatherMap API key not set."

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"The weather in {city} is {weather} with a temperature of {temp}°C."
    except requests.RequestException as e:
        return f"Error fetching weather for {city}: {str(e)}"

# Create the agent with Gemini model
agent = Agent(
    name="WeatherAssistant",
    instructions="You are a helpful assistant that provides weather information for cities. Use the get_weather tool to fetch current weather data when asked about the weather.",
    model=model,
    tools=[get_weather],
    output_type=UserINfo
)

# Main function to run the agent
async def main():
    result = await Runner.run(agent, "What's the weather in Pakistan(islamabad)?")
    # user_info = UserINfo.parse_obj(result.final_output)
    print(result.final_output)

# Run the agent
if __name__ == "__main__":
    asyncio.run(main())