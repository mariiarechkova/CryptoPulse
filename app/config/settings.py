import os

BYBIT_BASE_URL = os.getenv("BYBIT_BASE_URL", "https://api.bybit.com")


# --- LLM settings ---

LLM_ENABLED = os.getenv("LLM_ENABLED", "false").lower() == "true"

YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_MODEL_URI = os.getenv("YANDEX_MODEL_URI")
YANDEX_TIMEOUT_SECONDS = int(os.getenv("YANDEX_TIMEOUT_SECONDS", "20"))
YANDEX_RETRIES = int(os.getenv("YANDEX_RETRIES", "2"))

LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "25"))

# --- CryptoBot / CryptoPay ---

CRYPTOBOT_API_TOKEN = os.getenv("CRYPTOBOT_API_TOKEN")
CRYPTOBOT_BASE_URL = os.getenv("CRYPTOBOT_BASE_URL", "https://pay.crypt.bot/api")
CRYPTOBOT_TIMEOUT_SECONDS = int(os.getenv("CRYPTOBOT_TIMEOUT_SECONDS", "10"))

CRYPTOPAY_WEBHOOK_SECRET_PATH = os.getenv("CRYPTOPAY_WEBHOOK_SECRET_PATH")
CRYPTOPAY_WEBHOOK_VERIFY_SIGNATURE = os.getenv("CRYPTOPAY_WEBHOOK_VERIFY_SIGNATURE")
