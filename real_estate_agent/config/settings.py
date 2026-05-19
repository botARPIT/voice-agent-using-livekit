"""
Application configuration using Pydantic Settings.
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # LiveKit Configuration
    livekit_url: str = Field(..., description="LiveKit WebSocket URL")
    livekit_api_key: str = Field(..., description="LiveKit API key")
    livekit_api_secret: str = Field(..., description="LiveKit API secret")

    # Model Provider API Keys (optional if using LiveKit Inference)
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    google_api_key: Optional[str] = Field(default=None, description="Google/Gemini API key")
    deepgram_api_key: Optional[str] = Field(default=None, description="Deepgram API key")
    cartesia_api_key: Optional[str] = Field(default=None, description="Cartesia API key")
    elevenlabs_api_key: Optional[str] = Field(default=None, description="ElevenLabs API key")

    # Agent Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    stt_model: str = Field(default="deepgram/nova-3", description="STT model")
    llm_model: str = Field(default="openai/gpt-4.1-mini", description="LLM model")
    tts_model: str = Field(default="cartesia/sonic-3", description="TTS model")
    tts_voice: str = Field(
        default="71b6f7b2-5ae9-4d10-9f27-0e3b2d5f1c3a",
        description="TTS voice ID"
    )

    # Worker Configuration
    num_idle_processes: int = Field(default=2, description="Number of idle worker processes")
    min_interruption_duration: float = Field(default=0.5, description="Min interruption duration in seconds")

    # Business Configuration
    company_name: str = Field(default="DreamHome Realty", description="Company name")
    available_hours: str = Field(default="Monday-Saturday 9AM-6PM", description="Business hours")

    # Langfuse Configuration
    langfuse_public_key: Optional[str] = Field(default=None, description="Langfuse public key")
    langfuse_secret_key: Optional[str] = Field(default=None, description="Langfuse secret key")
    langfuse_host: str = Field(default="https://us.cloud.langfuse.com", description="Langfuse host URL")
    enable_langfuse: bool = Field(default=True, description="Enable Langfuse tracing")

    # Production Features
    enable_preemptive_generation: bool = Field(default=True, description="Enable preemptive generation (faster but less accurate)")
    enable_noise_cancellation: bool = Field(default=True, description="Enable noise cancellation")
    enable_semantic_turn_detection: bool = Field(default=True, description="Enable semantic turn detection")

    # Fallback Models
    llm_fallback_models: list[str] = Field(
        default=["google/gemini-2.5-flash", "openai/gpt-4.1-nano"],
        description="LLM fallback models"
    )
    stt_fallback_models: list[str] = Field(
        default=["assemblyai/universal-streaming", "deepgram/nova-2"],
        description="STT fallback models"
    )
    tts_fallback_models: list[str] = Field(
        default=["inworld/inworld-tts-1", "deepgram/aura-2"],
        description="TTS fallback models"
    )

    @property
    def is_livekit_inference(self) -> bool:
        """Check if using LiveKit Inference (no external API keys needed)."""
        return self.openai_api_key is None or self.openai_api_key == ""


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
