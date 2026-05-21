"""Groq LLM helper for the AI CRM backend."""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from groq import Groq

from config import settings

DECOMMISSIONED_GROQ_MODELS = {
    "gemma2-9b-it": "llama-3.3-70b-versatile",
    "gemma2-9b": "llama-3.3-70b-versatile",
    "gemma2-14b": "llama-3.3-70b-versatile",
    "gemma2-7b": "llama-3.3-70b-versatile",
}
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"


def normalize_groq_model(model: Optional[str] = None) -> str:
    raw_model = (model or settings.GROQ_MODEL or DEFAULT_GROQ_MODEL).strip()
    if not raw_model:
        return DEFAULT_GROQ_MODEL
    return DECOMMISSIONED_GROQ_MODELS.get(raw_model, raw_model)


def get_groq_client() -> Groq:
    return Groq(api_key=settings.GROQ_API_KEY)


def chat_completion(
    messages: List[Dict[str, str]],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    model: Optional[str] = None,
) -> str:
    temperature = settings.TEMPERATURE if temperature is None else temperature
    max_tokens = settings.MAX_TOKENS if max_tokens is None else max_tokens
    model_name = normalize_groq_model(model)

    client = get_groq_client()
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    return response.choices[0].message.content
