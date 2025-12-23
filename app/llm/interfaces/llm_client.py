from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 300,
    ) -> str:
        raise NotImplementedError