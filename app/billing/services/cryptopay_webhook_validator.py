from __future__ import annotations

import json
import logging
from typing import Any

from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)

from infrastructure.cryptobot.signature import verify_cryptopay_signature

logger = logging.getLogger(__name__)


class CryptoPayWebhookValidator:
    def __init__(
        self,
        *,
        expected_secret: str,
        verify_signature: bool,
        api_token: str,
    ) -> None:
        self._expected_secret = expected_secret
        self._verify_signature = verify_signature
        self._api_token = api_token

    def validate_secret(self, *, secret: str) -> int | None:
        if secret != self._expected_secret:
            return HTTP_404_NOT_FOUND
        return None

    def validate_signature(self, *, raw_body: bytes, signature: str | None) -> int | None:
        if not self._verify_signature:
            return None

        if not signature:
            logger.warning("CryptoPay webhook: missing signature")
            return HTTP_401_UNAUTHORIZED

        if not verify_cryptopay_signature(
            api_token=self._api_token,
            raw_body=raw_body,
            signature_hex=signature,
        ):
            logger.warning("CryptoPay webhook: bad signature")
            return HTTP_401_UNAUTHORIZED

        return None

    def parse_update(self, *, raw_body: bytes) -> dict[str, Any] | None:
        try:
            update = json.loads(raw_body.decode("utf-8"))
        except Exception:
            logger.warning("CryptoPay webhook: invalid json")
            return None

        if not isinstance(update, dict):
            logger.warning("CryptoPay webhook: json root is not object")
            return None

        return update
