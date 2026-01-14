import asyncio
import logging

from app.llm.interfaces.llm_client import LLMClient
from app.llm.prompts.explain_alert import build_explain_alert_prompt

logger = logging.getLogger(__name__)


class LLMService:

    def __init__(
        self,
        client: LLMClient,
        enabled: bool,
        timeout_seconds: int = 8,
    ) -> None:
        self._client = client
        self._enabled = enabled
        self._timeout_seconds = timeout_seconds

    async def _complete_safe(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 300,
        fallback: str = "",
    ) -> str:
        if not self._enabled:
            return fallback

        try:
            return await asyncio.wait_for(
                self._client.complete(
                    prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                ),
                timeout=self._timeout_seconds,
            )
        except Exception as e:
            logger.warning("LLM call failed: %s", e, exc_info=True)
            return fallback

    async def explain_alert(self, fallback_text: str) -> str:
        prompt = build_explain_alert_prompt(fallback_text)
        return await self._complete_safe(
            prompt,
            temperature=0.3,
            max_tokens=450,
            fallback=fallback_text,
        )
