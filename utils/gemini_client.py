"""Small compatibility wrapper around Google's current Gemini Python SDK.

It preserves the chat.complete interface used by the original LexAI modules,
so the existing three-agent workflow can be migrated with minimal changes.
"""
from dataclasses import dataclass
import os
from typing import Any


@dataclass
class _Message:
    content: str


@dataclass
class _Choice:
    message: _Message


@dataclass
class _ChatResponse:
    choices: list[_Choice]


class _ChatCompletions:
    def __init__(self, sdk_client: Any):
        self._client = sdk_client

    def complete(self, *, model: str | None = None, messages: list[dict],
                 max_tokens: int = 512, temperature: float = 0.2, **kwargs):
        prompt_parts = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            if role == "system":
                prompt_parts.append(f"Instructions:\n{content}")
            else:
                prompt_parts.append(str(content))
        response = self._client.models.generate_content(
            model=os.getenv("GEMINI_MODEL") or model or "gemini-3.5-flash-lite",
            contents="\n\n".join(prompt_parts),
            config={"temperature": temperature, "max_output_tokens": max_tokens},
        )
        return _ChatResponse(choices=[_Choice(message=_Message(content=response.text or ""))])


class GeminiClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing. Add it to your .env file.")
        try:
            from google import genai
        except ImportError as exc:
            raise ImportError("Gemini SDK missing. Run: pip install google-genai") from exc
        self._sdk_client = genai.Client(api_key=api_key)
        self.chat = type("Chat", (), {})()
        self.chat.complete = _ChatCompletions(self._sdk_client).complete

    def close(self):
        self._sdk_client.close()


def get_gemini_client(api_key: str | None = None) -> GeminiClient:
    return GeminiClient(api_key or os.getenv("GEMINI_API_KEY", ""))
