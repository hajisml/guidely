"""Shared Gemini client, with retry for the free tier's tight rate limits."""

import logging
import os
import re
import time
from functools import lru_cache
from typing import Callable, TypeVar

from google import genai
from google.genai import errors, types

log = logging.getLogger(__name__)


class MissingApiKeyError(RuntimeError):
    pass


REQUEST_TIMEOUT_MS = 30_000
MAX_RETRIES = 3
DEFAULT_BACKOFF_SECONDS = 15
SERVER_ERROR_BACKOFF_SECONDS = 8

T = TypeVar("T")


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    if not os.getenv("GEMINI_API_KEY"):
        raise MissingApiKeyError("GEMINI_API_KEY is not set, add it to backend/.env")
    return genai.Client(http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS))


def _retry_delay(exc: errors.ClientError) -> float:
    """Pull the server-suggested backoff out of a 429, falling back to a default."""
    try:
        for detail in exc.details["error"]["details"]:
            if match := re.match(r"(\d+(?:\.\d+)?)s", detail.get("retryDelay", "")):
                return float(match.group(1))
    except (KeyError, TypeError):
        pass
    return DEFAULT_BACKOFF_SECONDS


def call_with_retry(fn: Callable[[], T]) -> T:
    """Free-tier quotas are a handful of requests per minute, and the shared
    capacity occasionally 503s — retry both a couple of times before giving up.
    """
    for attempt in range(MAX_RETRIES):
        try:
            return fn()
        except errors.ClientError as exc:
            if exc.code != 429 or attempt == MAX_RETRIES - 1:
                raise
            delay = _retry_delay(exc)
            log.info("rate limited, retrying in %.0fs (attempt %d/%d)", delay, attempt + 1, MAX_RETRIES)
            time.sleep(delay)
        except errors.ServerError as exc:
            if attempt == MAX_RETRIES - 1:
                raise
            log.info("model unavailable (%s), retrying in %ds (attempt %d/%d)",
                      exc.code, SERVER_ERROR_BACKOFF_SECONDS, attempt + 1, MAX_RETRIES)
            time.sleep(SERVER_ERROR_BACKOFF_SECONDS)
    raise AssertionError("unreachable")
