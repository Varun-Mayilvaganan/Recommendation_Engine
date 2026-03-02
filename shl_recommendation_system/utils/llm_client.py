"""Provider-agnostic LLM client. Supports Gemini, NVIDIA NIM, Groq."""

from typing import Any

from dotenv import load_dotenv

load_dotenv()


def _get_gemini_client():
    import os

    import google.generativeai as genai

    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY not set in .env")
    genai.configure(api_key=key)
    return genai.GenerativeModel("gemini-2.0-flash")


def complete(prompt: str, provider: str = "gemini") -> str:
    """
    Send prompt to LLM and return raw text response.
    provider: gemini | nvidia | groq
    """
    provider = (provider or "gemini").lower()
    if provider == "gemini":
        model = _get_gemini_client()
        response = model.generate_content(prompt)
        return response.text or ""
    if provider == "nvidia":
        from openai import OpenAI

        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=__import__("os").getenv("NVIDIA_API_KEY"),
        )
        r = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct-v2",
            messages=[{"role": "user", "content": prompt}],
        )
        return r.choices[0].message.content or ""
    if provider == "groq":
        from openai import OpenAI

        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=__import__("os").getenv("GROQ_API_KEY"),
        )
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        return r.choices[0].message.content or ""
    raise ValueError(f"Unknown provider: {provider}")


def extract_json_from_response(text: str) -> dict[str, Any] | None:
    """Extract JSON object from LLM response (handles markdown, extra text)."""
    import json
    import re

    # Try to find {...} block
    match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    # Try ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    return None
