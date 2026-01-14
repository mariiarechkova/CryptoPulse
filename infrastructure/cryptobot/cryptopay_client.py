from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class CryptoPayInvoice:
    invoice_id: str
    pay_url: str
    asset: str
    amount: str
    raw: dict[str, Any]


class CryptoPayClient:
    def __init__(
        self,
        *,
        api_token: str,
        base_url: str = "https://pay.crypt.bot/api",
        timeout: float = 10.0,
    ) -> None:
        self._api_token = api_token
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def create_invoice(
        self,
        *,
        amount: str,
        asset: str,
        description: str,
        payload: str,
        expires_in: int | None = None,
        allow_comments: bool = False,
        allow_anonymous: bool = False,
    ) -> CryptoPayInvoice:
        headers = {"Crypto-Pay-API-Token": self._api_token}
        data: dict[str, Any] = {
            "amount": amount,
            "asset": asset,
            "description": description,
            "payload": payload,
            "allow_comments": allow_comments,
            "allow_anonymous": allow_anonymous,
        }
        if expires_in is not None:
            data["expires_in"] = expires_in

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.post(f"{self._base_url}/createInvoice", json=data, headers=headers)
            r.raise_for_status()
            body = r.json()

        if not body.get("ok") or "result" not in body:
            raise RuntimeError(f"CryptoPay createInvoice failed: {body}")

        result = body["result"]
        return CryptoPayInvoice(
            invoice_id=str(result["invoice_id"]),
            pay_url=str(result["pay_url"]),
            asset=str(result["asset"]),
            amount=str(result["amount"]),
            raw=result,
        )
