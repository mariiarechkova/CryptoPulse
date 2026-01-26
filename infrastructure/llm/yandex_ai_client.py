import asyncio
from dataclasses import dataclass

import httpx

from app.llm.interfaces.llm_client import LLMClient

YANDEX_COMPLETION_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


@dataclass(frozen=True, slots=True)
class YandexLLMConfig:
    api_key: str
    model_uri: str  # gpt://<folder_id>/yandexgpt-lite/latest
    timeout_seconds: float = 20.0
    retries: int = 2


class YandexLLMClient(LLMClient):
    def __init__(
        self, *, api_key: str, model_uri: str, timeout_seconds: float = 20.0, retries: int = 2
    ) -> None:
        self._cfg = YandexLLMConfig(
            api_key=api_key,
            model_uri=model_uri,
            timeout_seconds=timeout_seconds,
            retries=retries,
        )

    async def complete(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 300,
    ) -> str:
        payload = {
            "modelUri": self._cfg.model_uri,
            "completionOptions": {
                "stream": False,
                "temperature": float(temperature),
                "maxTokens": str(int(max_tokens)),
            },
            "messages": [
                {"role": "user", "text": prompt},
            ],
        }

        headers = {
            "Authorization": f"Api-Key {self._cfg.api_key}",
            "Content-Type": "application/json",
        }

        timeout = httpx.Timeout(self._cfg.timeout_seconds)

        last_exc: Exception | None = None
        for attempt in range(self._cfg.retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    resp = await client.post(YANDEX_COMPLETION_URL, json=payload, headers=headers)

                if resp.status_code in (429, 500, 502, 503, 504):
                    raise httpx.HTTPStatusError(
                        f"Yandex LLM transient status={resp.status_code}",
                        request=resp.request,
                        response=resp,
                    )
                if resp.status_code in (400, 401, 403):
                    raise RuntimeError(f"Yandex {resp.status_code}: {resp.text}")

                resp.raise_for_status()
                data = resp.json()

                result = data.get("result") or {}
                alternatives = result.get("alternatives") or []

                if not alternatives:
                    raise RuntimeError(f"Yandex LLM: empty alternatives. payload={data}")

                msg = alternatives[0].get("message") or {}
                text = (msg.get("text") or "").strip()
                text = text.replace("```", "").strip()
                if not text:
                    raise RuntimeError(f"Yandex LLM: empty text. payload={data}")

                return text

            except Exception as e:
                last_exc = e
                if attempt >= self._cfg.retries:
                    break
                await asyncio.sleep(0.5 * (2**attempt))

        raise RuntimeError("Yandex LLM request failed") from last_exc
