"""
The one place that talks to the AI provider.

Today this points at Google's Gemini API through its "OpenAI-compatible" address.
To switch provider later (for example GitHub Models, https://models.github.ai/inference),
change BASE_URL and the key and model names below. Nothing else needs to change.
"""
import base64
import mimetypes
import os
import re
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

_client = None


def get_client():
    """Create the client on first use, so a missing key shows a clear message."""
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is missing from your .env file.")
        _client = OpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
    return _client


def get_model_name():
    if not GEMINI_MODEL:
        raise RuntimeError("GEMINI_MODEL is missing from your .env file. Run: python test_llm.py models")
    return GEMINI_MODEL


# ---------- Retry rules ----------

def _status_code(exc):
    """Find the HTTP status code (402, 429, 503...) hiding inside an error, if there is one."""
    e, hops = exc, 0
    while e is not None and hops < 10:
        for holder in (e, getattr(e, "response", None)):
            code = getattr(holder, "status_code", None)
            if isinstance(code, int):
                return code
        e = e.__cause__ or e.__context__
        hops += 1
    # Last resort: some wrappers only keep the error text
    match = re.search(r"(?:Error code:|error '|status code[: ]*)\s*(\d{3})", str(exc), re.IGNORECASE)
    return int(match.group(1)) if match else None


def is_retryable(exc):
    """True only for temporary problems: 429 (slow down), 5xx (their server), network hiccups.
    Billing (402), bad key (401), forbidden (403) and bad requests (400) will fail again."""
    code = _status_code(exc)
    if code is not None:
        return code == 429 or 500 <= code < 600

    e, hops = exc, 0
    while e is not None and hops < 10:
        name = type(e).__name__
        if "Connection" in name or "Timeout" in name:
            return True
        e = e.__cause__ or e.__context__
        hops += 1
    return False


def call_with_retry(fn, max_attempts=3, base_delay=5):
    """Run fn(). If it fails with a temporary error, wait 5s, then 10s, and try again."""
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as e:
            if not is_retryable(e) or attempt == max_attempts:
                raise
            delay = base_delay * 2 ** (attempt - 1)
            print(f"Temporary error ({type(e).__name__}). Retry {attempt} of {max_attempts - 1} in {delay}s...")
            time.sleep(delay)


# ---------- Helpers the rest of the project uses ----------

def image_to_data_url(image_path):
    """Turn a local photo into text the API accepts (a base64 'data URL')."""
    mime = mimetypes.guess_type(image_path)[0] or "image/jpeg"
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def chat(messages, max_tokens=1024):
    """Send one chat request and return the answer text."""
    def _call():
        return get_client().chat.completions.create(
            model=get_model_name(), messages=messages, max_tokens=max_tokens
        )

    completion = call_with_retry(_call)
    text = completion.choices[0].message.content
    if not text:
        raise RuntimeError(
            "The model returned an empty answer. It may have used up max_tokens while thinking; "
            "try a higher max_tokens."
        )
    return text.strip()