"""
GenAI integration layer.

Kept separate from views/tasks so the LLM provider can be swapped
(OpenAI / Anthropic / local model) without touching business logic.
Demonstrates the "GenAI-related integrations" requirement from the JD.
"""
import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class GenAIService:
    """Thin wrapper around an LLM API for summarizing & tagging notes."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.GENAI_API_KEY
        self.model = model or settings.GENAI_MODEL

    def summarize_and_tag(self, text: str) -> dict:
        """
        Returns {"summary": str, "tags": list[str]}.
        Uses OpenAI's chat completions API as the example provider.
        Swap the request body for Anthropic/Gemini as needed.
        """
        if not self.api_key:
            # Safe fallback so the app still works without a real API key
            # (useful for local dev / demos).
            return self._fallback(text)

        try:
            import requests

            prompt = (
                "Summarize the following note in 2 sentences and suggest "
                "up to 5 short topic tags. Respond ONLY as JSON with keys "
                "'summary' and 'tags'.\n\nNote:\n" + text
            )
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                },
                timeout=30,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            data = json.loads(content)
            return {
                "summary": data.get("summary", ""),
                "tags": data.get("tags", []),
            }
        except Exception:
            logger.exception("GenAI call failed, falling back to naive summary")
            return self._fallback(text)

    @staticmethod
    def _fallback(text: str) -> dict:
        words = text.split()
        summary = " ".join(words[:25]) + ("..." if len(words) > 25 else "")
        tags = list({w.strip(".,!?").lower() for w in words if len(w) > 6})[:5]
        return {"summary": summary, "tags": tags}
