# Islamic Guidance Assistant

A comprehensive and intelligent AI-powered assistant designed to provide Islamic guidance based precisely on authentic sources including the Quran, established Tafsirs, and audio recitations. The project harnesses the reasoning capabilities of Gemini 2.5 Flash coupled with external tool-calling to ensure factual, contextually accurate, and scholarly responses. 

The application offers two interfaces: a built-in interactive **Chainlit** chat interface and a separate highly customizable **FastAPI/WebSocket** web interface.

---

## 🌟 Key Features
- **Accurate Quranic Advice**: Finds exact Arabic Ayats and English translations for specific themes or questions.
- **Tafsir Explanations**: Provides scholarly commentary and context directly gathered from official sources (default: The Clear Quran Tafsir).
- **Recitation Integration**: Fetches direct links to official Arabic recitations (default: Mishary Rashid Alafasy) so users can hear the verses.
- **Islamic Dates**: Real-time fetching of the current Islamic (Hijri) dates.
- **User Personalization**: Log in with your *Quran.com / Quran Foundation* account to allow the AI to access your bookmarks and recent reading sessions!
- **Web Browsing capability**: Uses Tavily search to answer general contemporary questions that fall outside strictly Quranic realms.

---

## 🛠️ Technology Stack & APIs

### 1. **Quran Foundation API (Crucial for Authenticity)**
The core source of absolute truth for all religious inquiries in this assistant. We specifically use `https://api.quran.com/api/v4` and `https://apis.quran.foundation/v1` for:
- **Search endpoint (`/search`)**: Allows the AI to query the Quran by topic, getting specific chapter and verse keys.
- **Tafsir endpoint (`/quran/tafsirs/169`)**: Ensures the AI doesn't hallucinate Islamic meaning by strictly sourcing 'The Clear Quran Tafsir' commentaries. 
- **Recitation endpoint (`/recitations/...`)**: Locates the direct `.mp3` audio URL corresponding precisely to the sought verse.
- **User Data (`/user/profile`, `/user/bookmarks`, `/user/reading_sessions`)**: Retrieves personalized cross-platform reading data if the user authenticates with Quran Foundation OAuth2.

### 2. **AI & Orchestration**
- **LLM Engine**: Google's `gemini-2.5-flash` model, driving logic and formatting.
- **Agent Framework**: Custom lightweight asynchronous agent structure (`agent_core.py`, `agent_setup.py`) wrapping OpenAI's compatibility specs.

### 3. **Other Tools**
- **Aladhan API `gToH` endpoint**: `http://api.aladhan.com/v1/gToH` reliably translates standard Gregorian dates requested by users to the concurrent Hijri (Islamic) dates.
- **Tavily API**: Powers generic current-events web searches explicitly when subjects fall outside the Quran's direct texts.

---

## 📋 Environment Configuration (`.env`)
Before running the project, you must set your environment variables. Create a `.env` file in the root directory:

```env
# Required AI API Keys
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# (Optional) Quran Foundation OAuth2 For Personalized History
OAUTH_QURAN_CLIENT_ID=your_quran_oauth_client_id_here
OAUTH_QURAN_CLIENT_SECRET=your_quran_oauth_client_secret_here
# Can override the auth URL if acting as a pre-live developer
# QURAN_OAUTH_BASE_URL=https://prelive-oauth2.quran.foundation 
```

---

## 🚀 How to Use & Run

1. **Install Requirements**
   Make sure Python is installed (preferably utilizing a `.venv` virtual environment). Install the necessary dependencies (like `fastapi`, `uvicorn`, `chainlit`, `httpx`, etc.).

2. **Interface Option A: The Custom Web UI (FastAPI & WebSockets)** 
   Starts a standalone custom frontend interacting over WebSockets perfectly with your custom logic.
   ```bash
   python server.py
   ```
   Navigate to `http://localhost:8080/` in your browser.

3. **Interface Option B: The Chainlit UI**
   Starts an interactive developer-centric Chat UI with seamless OAuth login capabilities and step-by-step reasoning visibility.
   ```bash
   chainlit run main.py -w
   ```
   Navigate to `http://localhost:8000/` in your browser.

4. **Run Headless Terminal Tests**
   You can easily test the underlying Agent functionality explicitly querying specific things from the terminal without starting a server:
   ```bash
   python test_agent.py
   ```

---

## 🏗️ Project Architecture overview
- `agent_core.py`: The system definitions and tool logic (API fetchers) containing the core system prompt that commands the agent to output strict Arabic formats.
- `agent_setup.py`: Identical logic structure but uniquely adapted to bind tools like `Bookmarks` relying specifically on Chainlit user-session auth tokens.
- `main.py`: The entry-point for the Chainlit UI implementation with custom `Auth0OAuthProvider` rewrites routing log-ins via the Quran Foundation server.
- `server.py`: The fallback standalone FastAPI logic for running WebSocket channels pointing locally hosted `/public` html folders.
- `test_agent.py`: A lightweight script used to rapidly debug system directives synchronously using `asyncio.run()`.
