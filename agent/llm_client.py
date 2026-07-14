"""
StudyMate AI — Groq LLM Client.

Wrapper around the Groq API for all LLM inference calls.
Supports primary and fallback models with retry logic.
"""

import json
from typing import Any, Optional

from groq import Groq, APIError, RateLimitError

from backend.config import get_settings
from backend.exceptions import LLMError
from utils.logger import get_logger
from utils.retry import retry_async

logger = get_logger("llm_client")


class LLMClient:
    """Client for Groq API LLM inference."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client: Optional[Groq] = None

    def _get_client(self) -> Groq:
        """Lazily initialize the Groq client."""
        if self._client is None:
            if not self._settings.groq_api_key:
                raise LLMError(
                    "GROQ_API_KEY not set. Please add it to your .env file."
                )
            self._client = Groq(api_key=self._settings.groq_api_key)
        return self._client

    @retry_async(
        max_attempts=3,
        base_delay=1.0,
        retryable_exceptions=(APIError, RateLimitError, ConnectionError),
    )
    async def generate(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
    ) -> str:
        """
        Generate a response from the LLM.

        Tries the primary model first, falls back to the secondary model
        if the primary fails.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            temperature: Sampling temperature (default from config).
            max_tokens: Maximum response tokens (default from config).
            model: Override model name.

        Returns:
            Generated text response.

        Raises:
            LLMError: If both primary and fallback models fail.
        """
        settings = self._settings
        temp = temperature if temperature is not None else settings.llm_temperature
        tokens = max_tokens if max_tokens is not None else settings.llm_max_tokens
        target_model = model or settings.llm_primary_model

        client = self._get_client()

        try:
            response = client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=temp,
                max_tokens=tokens,
            )

            content = response.choices[0].message.content
            logger.info(
                "LLM response generated (model=%s, tokens=%d)",
                target_model,
                response.usage.completion_tokens if response.usage else 0,
            )
            return content or ""

        except (APIError, RateLimitError) as exc:
            # Try fallback model
            if target_model != settings.llm_fallback_model:
                logger.warning(
                    "Primary model (%s) failed: %s. Trying fallback (%s)...",
                    target_model, exc, settings.llm_fallback_model,
                )
                try:
                    response = client.chat.completions.create(
                        model=settings.llm_fallback_model,
                        messages=messages,
                        temperature=temp,
                        max_tokens=tokens,
                    )
                    content = response.choices[0].message.content
                    logger.info(
                        "Fallback model response generated (model=%s)",
                        settings.llm_fallback_model,
                    )
                    return content or ""

                except Exception as fallback_exc:
                    logger.error("Fallback model also failed: %s", fallback_exc)
                    raise LLMError(
                        f"Both models failed. Primary: {exc}, Fallback: {fallback_exc}"
                    ) from fallback_exc

            raise LLMError(f"LLM API call failed: {exc}") from exc

    async def generate_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
    ) -> Optional[dict[str, Any]]:
        """
        Generate a JSON response from the LLM.

        Uses lower temperature for more deterministic JSON output.
        Attempts JSON parsing and repair if needed.

        Args:
            messages: List of message dicts.
            temperature: Lower temperature for structured output.

        Returns:
            Parsed JSON dict, or None if parsing fails after repair.
        """
        from utils.helpers import safe_json_parse
        from agent.prompts.json_repair_prompt import get_json_repair_prompt

        raw_response = await self.generate(messages, temperature=temperature)

        # Try direct parse
        parsed = safe_json_parse(raw_response)
        if parsed:
            return parsed

        # Attempt JSON repair via LLM
        logger.warning("JSON parse failed, attempting repair...")
        repair_prompt = get_json_repair_prompt(raw_response)
        repair_messages = [{"role": "user", "content": repair_prompt}]

        repaired_response = await self.generate(
            repair_messages, temperature=0.1, max_tokens=2048
        )

        parsed = safe_json_parse(repaired_response)
        if parsed:
            logger.info("JSON repair successful")
            return parsed

        logger.error("JSON repair also failed. Raw: %s", raw_response[:200])
        return None


# Singleton instance
llm_client = LLMClient()
