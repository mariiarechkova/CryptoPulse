import json
import logging
from typing import Any

from fastapi import FastAPI, Request, Response
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED
import app.billing.models  # noqa: F401

from app.billing.repositories.payment_repository import PaymentRepository
from app.billing.repositories.tariff_plan_repository import TariffPlanRepository
from app.billing.repositories.user_repository import UserRepository
from app.billing.services.payment_webhook_service import PaymentWebhookService
from app.config import settings
from infrastructure.cryptobot.signature import verify_cryptopay_signature
from infrastructure.db.session import async_session_maker
from infrastructure.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/webhooks/cryptopay/{secret}")
async def cryptopay_webhook(secret: str, request: Request) -> Response:
    if secret != settings.CRYPTOPAY_WEBHOOK_SECRET_PATH:
        return Response(status_code=HTTP_404_NOT_FOUND)

    raw = await request.body()

    signature = request.headers.get("crypto-pay-api-signature")
    if settings.CRYPTOPAY_WEBHOOK_VERIFY_SIGNATURE:
        if not signature:
            logger.warning("CryptoPay webhook: missing signature")
            return Response(status_code=HTTP_401_UNAUTHORIZED)

        ok = verify_cryptopay_signature(
            api_token=settings.CRYPTOBOT_API_TOKEN,
            raw_body=raw,
            signature_hex=signature,
        )
        if not ok:
            logger.warning("CryptoPay webhook: bad signature")
            return Response(status_code=HTTP_401_UNAUTHORIZED)

    try:
        update: dict[str, Any] = json.loads(raw.decode("utf-8"))
    except Exception:
        logger.warning("CryptoPay webhook: invalid json")
        return Response(status_code=HTTP_400_BAD_REQUEST)

    async with async_session_maker() as session:
        service = PaymentWebhookService(
            session=session,
            payment_repo=PaymentRepository(session),
            user_repo=UserRepository(session),
            tariff_repo=TariffPlanRepository(session),
        )
        result = await service.handle_update(update=update)

    logger.info("CryptoPay webhook handled", extra={"action": result.action})
    return Response(status_code=HTTP_200_OK)
