from openai import AsyncOpenAI

from app.llm.interfaces.llm_client import LLMClient


class OpenAIClient(LLMClient):

    def __init__(self, *, api_key: str, model: str) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def complete(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 300,
    ) -> str:
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content = resp.choices[0].message.content or ""
        return content.strip()
