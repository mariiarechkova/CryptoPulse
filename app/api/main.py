from fastapi import FastAPI

from app.billing.webhooks.cryptopay_webhook import router as cryptopay_router

app = FastAPI()

app.include_router(cryptopay_router)
