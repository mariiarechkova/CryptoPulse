import os

BYBIT_BASE_URL = os.getenv("BYBIT_BASE_URL", "https://api.bybit.com")


# --- LLM settings ---

LLM_ENABLED = os.getenv("LLM_ENABLED", "false").lower() == "true"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "8"))