"""
Local LLM Client

Simple client for calling a local LLM through an OpenAI-compatible API.
Defaults to Ollama at http://localhost:11434/v1

Supports graceful degradation if the local LLM is unavailable.
No cloud API keys required.
"""

import os
from typing import Any, Callable, Optional

import requests


DEFAULT_LOCAL_LLM_BASE_URL = "http://localhost:11434/v1"
DEFAULT_LOCAL_LLM_MODEL = "qwen2.5:7b-instruct"
DEFAULT_LOCAL_LLM_TIMEOUT = 30


def _parse_timeout(value: int | str | None) -> int:
    """Return a safe positive timeout value in seconds."""
    if value is None:
        return DEFAULT_LOCAL_LLM_TIMEOUT

    try:
        timeout = int(value)
    except (TypeError, ValueError):
        return DEFAULT_LOCAL_LLM_TIMEOUT

    if timeout <= 0:
        return DEFAULT_LOCAL_LLM_TIMEOUT
    return timeout


class LocalLLMClient:
    """
    Client for calling a local LLM through an OpenAI-compatible API.
    
    Defaults to Ollama running at localhost:11434/v1
    Model: qwen2.5:7b-instruct
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        http_post: Callable[..., Any] | None = None,
    ):
        """
        Initialize the local LLM client.
        
        Args:
            base_url: Base URL for the OpenAI-compatible API.
                     Defaults to env var LOCAL_LLM_BASE_URL or http://localhost:11434/v1
            model: Model name to use.
                  Defaults to env var LOCAL_LLM_MODEL or qwen2.5:7b-instruct
            timeout: Request timeout in seconds.
                    Defaults to env var LOCAL_LLM_TIMEOUT or 30
        """
        configured_base_url = (
            base_url
            or os.getenv("LOCAL_LLM_BASE_URL")
            or DEFAULT_LOCAL_LLM_BASE_URL
        )
        self.model = model or os.getenv("LOCAL_LLM_MODEL") or DEFAULT_LOCAL_LLM_MODEL
        self.timeout = _parse_timeout(
            timeout if timeout is not None else os.getenv("LOCAL_LLM_TIMEOUT")
        )
        self.base_url = configured_base_url.rstrip("/")
        self._http_post = http_post or requests.post

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.2,
    ) -> dict:
        """
        Call the local LLM with the given messages.
        
        Args:
            messages: List of message dicts with "role" and "content" keys
            temperature: Sampling temperature (0.0 to 1.0)
        
        Returns:
            Normalized response dict:
            {
                "ok": True/False,
                "model": "model-name",
                "content": "response text or empty string",
                "error": "error message if ok=False, optional",
                "raw": {"original": "response dict"}
            }
        """
        if not messages:
            return {
                "ok": False,
                "model": self.model,
                "content": "",
                "error": "No messages provided",
                "raw": {},
            }

        try:
            # Build the OpenAI-compatible API request
            url = f"{self.base_url}/chat/completions"
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }

            response = self._http_post(
                url,
                json=payload,
                timeout=self.timeout,
            )

            # Handle HTTP errors
            if response.status_code != 200:
                return {
                    "ok": False,
                    "model": self.model,
                    "content": "",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "raw": {},
                }

            # Parse response
            data = response.json()

            # Extract content from OpenAI-compatible response format
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                if "message" in choice:
                    content = choice["message"].get("content", "")
                    return {
                        "ok": True,
                        "model": self.model,
                        "content": content,
                        "raw": data,
                    }

            return {
                "ok": False,
                "model": self.model,
                "content": "",
                "error": "Unexpected response format",
                "raw": data,
            }

        except requests.exceptions.Timeout:
            return {
                "ok": False,
                "model": self.model,
                "content": "",
                "error": f"Request timeout after {self.timeout}s",
                "raw": {},
            }
        except requests.exceptions.ConnectionError as e:
            return {
                "ok": False,
                "model": self.model,
                "content": "",
                "error": f"Connection error: {str(e)}",
                "raw": {},
            }
        except Exception as e:
            return {
                "ok": False,
                "model": self.model,
                "content": "",
                "error": f"Unexpected error: {str(e)}",
                "raw": {},
            }
