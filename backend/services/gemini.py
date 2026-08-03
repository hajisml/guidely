"""Shared Gemini client."""

import os
from functools import lru_cache

from google import genai


class MissingApiKeyError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    if not os.getenv("GEMINI_API_KEY"):
        raise MissingApiKeyError("GEMINI_API_KEY is not set, add it to backend/.env")
    return genai.Client()
