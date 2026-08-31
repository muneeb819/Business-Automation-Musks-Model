from typing import Any, Dict, List, Optional
import httpx
from app.core.config import settings


class AIService:
    """Provider-agnostic AI service layer."""

    def __init__(self, provider: str = "openai"):
        self.provider = provider
        self.model = settings.AI_MODEL
        self.api_key = settings.OPENAI_API_KEY

    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        if self.provider == "openai":
            return await self._call_openai(messages, temperature, max_tokens)
        raise ValueError(f"Unknown AI provider: {self.provider}")

    async def _call_openai(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        if not self.api_key:
            return self._mock_response(messages)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    def _mock_response(self, messages: List[Dict[str, str]]) -> str:
        last_message = messages[-1]["content"] if messages else ""
        return f"[Mock AI Response to: {last_message[:100]}...]"

    async def generate_structured(
        self,
        prompt: str,
        system_prompt: str = "You are an expert business development AI system.",
        temperature: float = 0.5,
    ) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        return await self.generate(messages, temperature)

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str = "You are an expert business development AI system. Always respond with valid JSON only.",
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """Generate a structured JSON result, used for scoring/enrichment/proposals."""
        if self.provider != "openai":
            raise ValueError(f"Unknown AI provider: {self.provider}")

        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured. Set it to enable real AI generation."
            )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]

        try:
            import json as _json

            return _json.loads(content)
        except Exception:
            return {"raw": content}


ai_service = AIService()
