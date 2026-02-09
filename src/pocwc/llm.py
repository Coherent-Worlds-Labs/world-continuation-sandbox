from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class LLMAdapter(Protocol):
    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 900,
    ) -> dict[str, Any]:
        ...


@dataclass(slots=True)
class LLMSettings:
    provider: str = "none"
    model: str = ""
    base_url: str = "https://openrouter.ai/api/v1"
    api_key: str = ""
    app_name: str = "pocwc-prototype"
    site_url: str = "http://localhost"
    timeout_seconds: int = 30

    @property
    def enabled(self) -> bool:
        return self.provider != "none" and bool(self.model) and bool(self.api_key)

    @classmethod
    def from_env(
        cls,
        *,
        provider_override: str | None = None,
        model_override: str | None = None,
        base_url_override: str | None = None,
    ) -> "LLMSettings":
        provider = (provider_override or os.getenv("POCWC_LLM_PROVIDER", "none")).strip().lower()
        model = (model_override or os.getenv("OPENROUTER_MODEL", "")).strip()
        base_url = (base_url_override or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")).strip()
        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        app_name = os.getenv("POCWC_APP_NAME", "pocwc-prototype").strip() or "pocwc-prototype"
        site_url = os.getenv("POCWC_SITE_URL", "http://localhost").strip() or "http://localhost"
        timeout_raw = os.getenv("POCWC_LLM_TIMEOUT", "30").strip()
        timeout_seconds = int(timeout_raw) if timeout_raw.isdigit() else 30

        if provider not in {"none", "openrouter"}:
            provider = "none"

        return cls(
            provider=provider,
            model=model,
            base_url=base_url.rstrip("/"),
            api_key=api_key,
            app_name=app_name,
            site_url=site_url,
            timeout_seconds=max(5, min(timeout_seconds, 120)),
        )


class OpenRouterAdapter:
    def __init__(self, settings: LLMSettings) -> None:
        self.settings = settings
        self.endpoint = f"{settings.base_url}/chat/completions"

    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 900,
    ) -> dict[str, Any]:
        payload = {
            "model": self.settings.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }
        body = json.dumps(payload).encode("utf-8")

        req = Request(
            self.endpoint,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.settings.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.settings.site_url,
                "X-Title": self.settings.app_name,
            },
        )
        try:
            with urlopen(req, timeout=self.settings.timeout_seconds) as resp:
                response_payload = json.loads(resp.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"OpenRouter request failed: {exc}") from exc

        try:
            content = response_payload["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError("OpenRouter response does not contain valid JSON content") from exc


def create_llm_adapter(settings: LLMSettings) -> LLMAdapter | None:
    if not settings.enabled:
        return None
    if settings.provider == "openrouter":
        return OpenRouterAdapter(settings)
    return None

