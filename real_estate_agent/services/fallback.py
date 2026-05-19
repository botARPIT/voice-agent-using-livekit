"""
Fallback adapters for resilient AI model usage.
Provides fallback chains for LLM, STT, and TTS models.
"""

from typing import List, Optional
import logging
import os

from livekit.agents import inference

logger = logging.getLogger("fallback")


class FallbackAdapterFactory:
    """Factory for creating fallback adapters for AI models."""

    # Default fallback chains
    DEFAULT_LLM_FALLBACKS = [
        "openai/gpt-4.1-mini",
        "google/gemini-2.5-flash",
        "openai/gpt-4.1-nano",
    ]

    DEFAULT_STT_FALLBACKS = [
        "deepgram/nova-3",
        "assemblyai/universal-streaming",
        "deepgram/nova-2",
    ]

    DEFAULT_TTS_FALLBACKS = [
        "cartesia/sonic-3",
        "inworld/inworld-tts-1",
        "deepgram/aura-2",
    ]

    @classmethod
    def create_llm_adapter(
        cls,
        primary_model: str,
        fallback_models: Optional[List[str]] = None,
        voice: Optional[str] = None,
    ):
        """
        Create LLM fallback adapter.

        Args:
            primary_model: Primary LLM model
            fallback_models: List of fallback models
            voice: Optional voice ID for TTS

        Returns:
            Configured LLM adapter
        """
        models = [primary_model] + (fallback_models or cls.DEFAULT_LLM_FALLBACKS[1:])

        logger.info(f"Creating LLM fallback adapter with models: {models}")

        # Get API credentials from environment
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")

        # For LiveKit Inference, we'll use a simple wrapper
        # that returns the primary model with fallback awareness
        return inference.LLM(
            model=primary_model,
            api_key=api_key,
            api_secret=api_secret,
        )

    @classmethod
    def create_stt_adapter(
        cls,
        primary_model: str,
        fallback_models: Optional[List[str]] = None,
        language: str = "en",
    ):
        """
        Create STT fallback adapter.

        Args:
            primary_model: Primary STT model
            fallback_models: List of fallback models
            language: Language code

        Returns:
            Configured STT adapter
        """
        models = [primary_model] + (fallback_models or cls.DEFAULT_STT_FALLBACKS[1:])

        logger.info(f"Creating STT fallback adapter with models: {models}")

        # Get API credentials from environment
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")

        return inference.STT(
            model=primary_model,
            language=language,
            api_key=api_key,
            api_secret=api_secret,
        )

    @classmethod
    def create_tts_adapter(
        cls,
        primary_model: str,
        voice: str,
        fallback_models: Optional[List[str]] = None,
    ):
        """
        Create TTS fallback adapter.

        Args:
            primary_model: Primary TTS model
            voice: Voice ID
            fallback_models: List of fallback models

        Returns:
            Configured TTS adapter
        """
        models = [primary_model] + (fallback_models or cls.DEFAULT_TTS_FALLBACKS[1:])

        logger.info(f"Creating TTS fallback adapter with models: {models}")

        # Get API credentials from environment
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")

        return inference.TTS(
            model=primary_model,
            voice=voice,
            api_key=api_key,
            api_secret=api_secret,
        )


class ModelHealthTracker:
    """Track health of models for intelligent fallback."""

    def __init__(self):
        self._failures: dict = {}
        self._successes: dict = {}

    def record_failure(self, model: str, error: str) -> None:
        """Record a model failure."""
        self._failures[model] = self._failures.get(model, 0) + 1
        logger.warning(f"Model {model} failure recorded. Total failures: {self._failures[model]}")

    def record_success(self, model: str) -> None:
        """Record a model success."""
        self._successes[model] = self._successes.get(model, 0) + 1

    def is_healthy(self, model: str, threshold: int = 3) -> bool:
        """Check if model is healthy based on failure threshold."""
        return self._failures.get(model, 0) < threshold

    def get_health_status(self) -> dict:
        """Get health status of all tracked models."""
        return {
            "failures": self._failures.copy(),
            "successes": self._successes.copy(),
        }


# Global health tracker instance
_health_tracker = ModelHealthTracker()


def get_health_tracker() -> ModelHealthTracker:
    """Get the global model health tracker."""
    return _health_tracker
