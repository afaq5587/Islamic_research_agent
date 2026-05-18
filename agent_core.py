import os
import json
import datetime
import httpx
from dotenv import load_dotenv
from agents import (
    Agent,
    function_tool,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_default_openai_client,
    set_tracing_disabled
)

# Load environment variables from .env file
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Using gemini-2.5-flash for the best balance of reasoning, speed, and tool-calling stability
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)
    
set_default_openai_client(external_client)
set_tracing_disabled(True)

# Quran Foundation API Configuration
QURAN_API_BASE = "https://api.quran.com/api/v4"

@function_tool
async def search_tavily(query: str) -> str:
    """
    Search the web for the latest updates, news, or general information using Tavily.
    Use this for topics not covered by the Quranic tools.
    """
    if not tavily_api_key:
        return "Error: Tavily API key not found."
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": tavily_api_key,
                "query": query,
                "search_depth": "advanced",
                "max_results": 5
            }
        )
        response.raise_for_status()
        return json.dumps(response.json().get("results", []))

@function_tool
async def search_quran(query: str) -> str:
    """
    Search for Quranic verses related to the query using the official Quran.com API.
    Returns a list of matching verses with their text and verse keys.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{QURAN_API_BASE}/search",
            params={"q": query, "language": "en"}
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("search", {}).get("results", [])
        return json.dumps(results[:5])

@function_tool
async def get_verse_explanation(verse_key: str, tafsir_id: int = 169) -> str:
    """
    Fetch the Tafsir (scholarly explanation) for a specific verse key (e.g., '2:255').
    Default tafsir_id 169 is 'The Clear Quran Tafsir'.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{QURAN_API_BASE}/quran/tafsirs/{tafsir_id}",
            params={"verse_key": verse_key}
        )
        response.raise_for_status()
        return json.dumps(response.json().get("tafsir", {}))

@function_tool
async def get_verse_audio(verse_key: str, reciter_id: int = 7) -> str:
    """
    Get the audio recitation link for a specific verse.
    Default reciter_id 7 is Mishary Rashid Alafasy.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{QURAN_API_BASE}/recitations/{reciter_id}/by_ayah/{verse_key}"
        )
        response.raise_for_status()
        audio_url = response.json().get("audio_files", [{}])[0].get("url")
        if audio_url:
            return f"https://audio.quran.com/{audio_url}"
        return "Audio not found."

@function_tool
async def get_current_date_and_time() -> str:
    """
    Get the current Gregorian date, time, and the corresponding Islamic (Hijri) date.
    Use this whenever a user asks for the current date, time, or Islamic date.
    """
    now = datetime.datetime.now()
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%H:%M:%S")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"http://api.aladhan.com/v1/gToH/{date_str}")
            if response.status_code == 200:
                data = response.json().get("data", {}).get("hijri", {})
                hijri_date = f"{data.get('day')} {data.get('month', {}).get('en')} {data.get('year')}"
                return f"Current Time: {time_str}\\nGregorian Date: {date_str}\\nIslamic (Hijri) Date: {hijri_date}"
        except Exception:
            pass
    return f"Current Time: {time_str}\\nGregorian Date: {date_str}"

agent = Agent(
    name="IslamicGuidanceAgent",
    instructions=(
        "You are a knowledgeable and empathetic Islamic guidance assistant specializing in the Quran. "
        "Your goal is to provide deep insights using the Quran, Tafsir, and recitations. You can also search the web for the latest updates.\n\n"
        "Research Capabilities:\n"
        "1. **Quran Search**: Use `search_quran` to find verses based on keywords or concepts.\n"
        "2. **Tafsir**: Use `get_verse_explanation` to provide scholarly context and detailed meanings of verses. NEVER rely on general knowledge; always pull from the Tafsir tool for accuracy.\n"
        "3. **Audio**: Use `get_verse_audio` to provide recitation links when a user wants to hear a verse.\n"
        "4. **Date & Time**: Use `get_current_date_and_time` to get the current Gregorian date, Hijri date, or time when requested.\n"
        "5. **Web Search**: Use `search_tavily` for latest updates, news, or information not covered by Quranic tools.\n\n"
        "Guidelines:\n"
        "- Prioritize Quranic sources for religious questions.\n"
        "- Use `search_tavily` for current events or general knowledge outside the Quran.\n"
        "- When providing a verse, aim to include its Tafsir context using `get_verse_explanation` to ensure a correct and scholarly understanding.\n"
        "- CRITICAL: ALWAYS provide the exact Arabic textual verses alongside their translations when referencing the Quran. Do NOT just summarize the Ayat, you MUST provide the specific Arabic text.\n"
        "- Always be respectful and professional.\n"
        "- Format responses clearly using markdown with headings, bold text, and organized sections."
    ),
    tools=[
        search_quran,
        get_verse_explanation,
        get_verse_audio,
        search_tavily,
        get_current_date_and_time,
    ],
    model=model
)
