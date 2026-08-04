"""Shared Gemini client."""

import os
from functools import lru_cache

from google import genai
from google.genai import types


class MissingApiKeyError(RuntimeError):
    pass


REQUEST_TIMEOUT_MS = 30_000


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    if not os.getenv("GEMINI_API_KEY"):
        raise MissingApiKeyError("GEMINI_API_KEY is not set, add it to backend/.env")
    return genai.Client(http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS))
