
import os
import httpx
from typing import Dict, Tuple
from dotenv import load_dotenv

# Load environment variables as early as possible
load_dotenv()

import chainlit as cl
from chainlit.oauth_providers import Auth0OAuthProvider, providers
from chainlit.user import User
from agent_setup import agent
from agents import Runner

# --- Quran Foundation OIDC Provider (Custom Implementation) ---
class QuranFoundationProvider(Auth0OAuthProvider):
    id = "quran-foundation"
    name = "Quran Foundation"
    icon = "https://quran.com/favicon.ico"
    env = ["OAUTH_QURAN_CLIENT_ID", "OAUTH_QURAN_CLIENT_SECRET"]

    def __init__(self):
        self.client_id = os.getenv("OAUTH_QURAN_CLIENT_ID")
        self.client_secret = os.getenv("OAUTH_QURAN_CLIENT_SECRET")
        
        # Use the specific pre-live base URL for Quran Foundation
        oauth_base = os.getenv("QURAN_OAUTH_BASE_URL", "https://prelive-oauth2.quran.foundation").rstrip("/")
        
        self.authorize_url = f"{oauth_base}/oauth2/auth"
        self.token_url = f"{oauth_base}/oauth2/token"
        self.user_info_url = f"{oauth_base}/userinfo"
        
        # Minimal authorize params - some OAuth providers are strict about these
        self.authorize_params = {
            "scope": "openid profile email",
            "response_type": "code"
        }

    async def get_token(self, code: str, url: str) -> str:
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": url,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, json=payload)
            response.raise_for_status()
            return response.json().get("access_token")

    async def get_user_info(self, token: str) -> Tuple[Dict, User]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_info_url,
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            raw_user_data = response.json()
            
            user = User(
                identifier=raw_user_data.get("sub") or raw_user_data.get("email"),
                metadata={
                    "name": raw_user_data.get("name") or f"{raw_user_data.get('first_name', '')} {raw_user_data.get('last_name', '')}".strip(),
                    "email": raw_user_data.get("email"),
                    "access_token": token,
                    "provider": self.id
                }
            )
            return raw_user_data, user

# Register the provider only if credentials are available
if os.getenv("OAUTH_QURAN_CLIENT_ID") and os.getenv("OAUTH_QURAN_CLIENT_SECRET"):
    try:
        providers.append(QuranFoundationProvider())
    except Exception as e:
        print(f"Warning: Could not register QuranFoundationProvider: {e}")

@cl.oauth_callback
def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: Dict[str, str],
    default_user: User,
) -> User:
    """
    Handle the OAuth callback and return the user object.
    """
    # Ensure the access token is in the metadata for later use
    default_user.metadata["access_token"] = token
    return default_user

MAX_MEMORY = 5

@cl.on_chat_start
async def start():
    # Store access token in session for tools to use
    user = cl.user_session.get("user")
    if user:
        # Access token was stored in metadata by oauth_callback
        token = user.metadata.get("access_token")
        cl.user_session.set("access_token", token)
    
    cl.user_session.set("memory", [])
    
    welcome_msg = "🤲 **Welcome to the Islamic Guidance Assistant!**\n\n"
    if user:
        welcome_msg += f"Logged in as **{user.identifier}**. I can now access your Quran.com bookmarks and reading history.\n"
    else:
        welcome_msg += (
            "I can answer your questions about the Quran and provide scholarly insights. "
            "For a personalized experience, please log in via the sidebar to access your Quran.com data."
        )
        
    await cl.Message(content=welcome_msg).send()

@cl.on_message
async def handle_message(message: cl.Message):
    query = message.content
    memory = cl.user_session.get("memory", [])

    context_prompt = ""
    if memory:
        context_prompt += "Previous questions and answers:\n"
        for i, (q, a) in enumerate(memory[-MAX_MEMORY:], 1):
            context_prompt += f"\nQ{i}: {q}\nA{i}: {a}\n"

    contextual_query = context_prompt + f"\nNow answer this: {query}"

    async with cl.Step(name="Agent Thinking") as step:
        result = await Runner.run(agent, input=contextual_query)
        step.output = result.final_output

    await cl.Message(content=result.final_output).send()

    memory.append((query, result.final_output))
    cl.user_session.set("memory", memory)
