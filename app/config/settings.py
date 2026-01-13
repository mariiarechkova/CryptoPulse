import os

BYBIT_BASE_URL = os.getenv("BYBIT_BASE_URL", "https://api.bybit.com")


# --- LLM settings ---

LLM_ENABLED = os.getenv("LLM_ENABLED", "false").lower() == "true"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "8"))

# --- CryptoBot / CryptoPay ---

CRYPTOBOT_API_TOKEN = os.getenv("CRYPTOBOT_API_TOKEN")
CRYPTOBOT_BASE_URL = os.getenv("CRYPTOBOT_BASE_URL", "https://pay.crypt.bot/api")
CRYPTOBOT_TIMEOUT_SECONDS = int(os.getenv("CRYPTOBOT_TIMEOUT_SECONDS", "10"))

CRYPTOPAY_WEBHOOK_SECRET_PATH = os.getenv("CRYPTOPAY_WEBHOOK_SECRET_PATH")
CRYPTOPAY_WEBHOOK_VERIFY_SIGNATURE = os.getenv("CRYPTOPAY_WEBHOOK_VERIFY_SIGNATURE")