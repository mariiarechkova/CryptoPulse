import logging

from fastapi import APIRouter, Request, Response
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
)

import app.billing.models  # noqa: F401
from app.billing.repositories.payment_repository import PaymentRepository
from app.billing.repositories.tariff_plan_repository import TariffPlanRepository
from app.billing.repositories.user_repository import UserRepository
from app.billing.services.cryptopay_webhook_validator import CryptoPayWebhookValidator
from app.billing.services.payment_webhook_service import PaymentWebhookService
from app.config import settings
from infrastructure.db.session import async_session_maker
from infrastructure.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/webhooks/cryptopay/{secret}")
async def cryptopay_webhook(secret: str, request: Request) -> Response:
    validator = CryptoPayWebhookValidator(
        expected_secret=settings.CRYPTOPAY_WEBHOOK_SECRET_PATH,
        verify_signature=settings.CRYPTOPAY_WEBHOOK_VERIFY_SIGNATURE,
        api_token=settings.CRYPTOBOT_API_TOKEN,
    )

    secret_status = validator.validate_secret(secret=secret)
    if secret_status is not None:
        return Response(status_code=secret_status)

    raw_body = await request.body()

    signature_status = validator.validate_signature(
        raw_body=raw_body,
        signature=request.headers.get("crypto-pay-api-signature"),
    )
    if signature_status is not None:
        return Response(status_code=signature_status)

    update = validator.parse_update(raw_body=raw_body)
    if update is None:
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
