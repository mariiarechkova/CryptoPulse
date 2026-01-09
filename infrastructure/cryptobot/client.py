from app.config.settings import (
    CRYPTOBOT_API_TOKEN,
    CRYPTOBOT_BASE_URL,
    CRYPTOBOT_TIMEOUT_SECONDS,
)
from infrastructure.cryptobot.cryptopay_client import CryptoPayClient

cryptopay_client = CryptoPayClient(
    api_token=CRYPTOBOT_API_TOKEN,
    base_url=CRYPTOBOT_BASE_URL,
    timeout=CRYPTOBOT_TIMEOUT_SECONDS,
)