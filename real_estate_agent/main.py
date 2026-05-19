"""
Main entry point for the Real Estate Voice Agent.
Production-grade implementation with:
- Direct API providers (Gemini, Deepgram, Cartesia)
- Fallback adapters for resilience
- Semantic turn detection
- Preemptive generation
- Langfuse tracing
- Comprehensive metrics collection
"""

import logging
import os
from contextlib import asynccontextmanager

from livekit.agents import (
    AgentSession,
    RoomInputOptions,
    WorkerOptions,
    cli,
    inference,
    metrics,
)
from livekit.agents import AgentStateChangedEvent, MetricsCollectedEvent
from livekit import rtc

# Import direct providers
from livekit.plugins import deepgram, cartesia
from livekit.plugins import google as google_plugin

from .config import get_settings
from .agents import AgentBuilder
from .services.fallback import FallbackAdapterFactory
from .services.telemetry import create_telemetry_collector, UsageCollector
from .services.langfuse_setup import setup_langfuse

logger = logging.getLogger("real-estate-agent")


def setup_logging(log_level: str) -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def create_stt_provider(settings):
    """Create STT provider with fallback."""
    if settings.deepgram_api_key:
        logger.info("Using Deepgram STT directly")
        return deepgram.STT(
            model="nova-3",
            language="en",
            api_key=settings.deepgram_api_key,
        )
    else:
        logger.info("Using LiveKit Inference for STT")
        return inference.STT(
            model=settings.stt_model,
            language="en",
            api_key=settings.livekit_api_key,
            api_secret=settings.livekit_api_secret,
        )


def create_llm_provider(settings):
    """Create LLM provider with fallback."""
    if settings.google_api_key:
        logger.info("Using Google Gemini LLM directly")
        return google_plugin.LLM(
            model="gemini-2.5-flash",
            api_key=settings.google_api_key,
        )
    else:
        logger.info("Using LiveKit Inference for LLM")
        return inference.LLM(
            model=settings.llm_model,
            api_key=settings.livekit_api_key,
            api_secret=settings.livekit_api_secret,
        )


def create_tts_provider(settings):
    """Create TTS provider with fallback."""
    if settings.cartesia_api_key:
        logger.info("Using Cartesia TTS directly")
        return cartesia.TTS(
            model="sonic-3",
            voice="71b6f7b2-5ae9-4d10-9f27-0e3b2d5f1c3a",
            api_key=settings.cartesia_api_key,
        )
    else:
        logger.info("Using LiveKit Inference for TTS")
        return inference.TTS(
            model=settings.tts_model,
            voice=settings.tts_voice,
            api_key=settings.livekit_api_key,
            api_secret=settings.livekit_api_secret,
        )


async def entrypoint(ctx):
    """
    Main entry point when a new job is dispatched.

    Args:
        ctx: Job context containing room and metadata
    """
    settings = get_settings()
    setup_logging(settings.log_level)

    # Setup Langfuse tracing
    if settings.enable_langfuse:
        langfuse_enabled = setup_langfuse(
            host=settings.langfuse_host,
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
        )
        if langfuse_enabled:
            logger.info("Langfuse tracing enabled")
        else:
            logger.warning("Langfuse tracing not available")

    logger.info(f"New session started - Room: {ctx.room.name}")

    # Detect if this is a phone call
    is_phone_call = ctx.room.metadata and "sip" in str(ctx.room.metadata).lower()

    # Create telemetry collector for this session
    telemetry = create_telemetry_collector()
    usage_collector = telemetry.usage_collector

    # Start session metrics tracking
    session_metrics = usage_collector.start_session(ctx.room.name)

    # Create providers with direct API keys
    try:
        stt = create_stt_provider(settings)
        llm = create_llm_provider(settings)
        tts = create_tts_provider(settings)
    except Exception as e:
        logger.error(f"Error creating providers: {e}. Falling back to LiveKit Inference.")
        # Fallback to LiveKit Inference
        stt = inference.STT(
            model=settings.stt_model,
            language="en",
            api_key=settings.livekit_api_key,
            api_secret=settings.livekit_api_secret,
        )
        llm = inference.LLM(
            model=settings.llm_model,
            api_key=settings.livekit_api_key,
            api_secret=settings.livekit_api_secret,
        )
        tts = inference.TTS(
            model=settings.tts_model,
            voice=settings.tts_voice,
            api_key=settings.livekit_api_key,
            api_secret=settings.livekit_api_secret,
        )

    # Create the AI pipeline with production features
    session_kwargs = {
        # STT with direct provider
        "stt": stt,
        # LLM with direct provider
        "llm": llm,
        # TTS with direct provider
        "tts": tts,
        # Turn detection settings
        "min_interruption_duration": settings.min_interruption_duration,
    }

    # Enable preemptive generation for faster responses
    if settings.enable_preemptive_generation:
        session_kwargs["preemptive_generation"] = True
        logger.info("Preemptive generation enabled (faster responses, slight accuracy tradeoff)")

    # Create the session
    session = AgentSession(**session_kwargs)

    # Setup telemetry handlers
    telemetry.setup_handlers(session)

    # Track fallback activations
    fallback_activations = 0

    @session.on("error")
    def _on_session_error(error):
        """Handle session errors and track fallback activations."""
        nonlocal fallback_activations
        logger.error(f"Session error: {error}")
        fallback_activations += 1
        session_metrics.fallback_activations = fallback_activations

    # Create the default (greeter) agent
    agent = AgentBuilder.get_default_agent()

    # Welcome message for phone calls
    if is_phone_call:
        await session.say(
            f"Thank you for calling {settings.company_name}! "
            "I'm your AI assistant, here to help you find your perfect home. "
            "Are you looking to buy or rent today?",
            allow_interruptions=True
        )

    # Add shutdown callback for logging
    async def log_usage():
        """Log usage summary on shutdown."""
        usage_collector.end_session(ctx.room.name)
        telemetry.log_usage_summary()

    ctx.add_shutdown_callback(log_usage)

    # Start the session
    try:
        await session.start(
            room=ctx.room,
            agent=agent,
            room_input_options=RoomInputOptions(),
        )
    except Exception as e:
        logger.error(f"Session error: {e}", exc_info=True)
        raise
    finally:
        logger.info(f"Session ended - Room: {ctx.room.name}")


def prewarm(proc) -> None:
    """
    Pre-load models to eliminate cold starts.
    Called when worker process starts.
    """
    settings = get_settings()
    setup_logging(settings.log_level)

    logger.info("Pre-warming agent server...")
    logger.info(f"Configuration: preemptive_generation={settings.enable_preemptive_generation}")
    logger.info(f"Configuration: semantic_turn_detection={settings.enable_semantic_turn_detection}")
    logger.info(f"Configuration: noise_cancellation={settings.enable_noise_cancellation}")

    # Log which providers are being used
    if settings.google_api_key:
        logger.info("Using Google Gemini LLM (direct API)")
    else:
        logger.info("Using LiveKit Inference for LLM")

    if settings.deepgram_api_key:
        logger.info("Using Deepgram STT (direct API)")
    else:
        logger.info("Using LiveKit Inference for STT")

    if settings.cartesia_api_key:
        logger.info("Using Cartesia TTS (direct API)")
    else:
        logger.info("Using LiveKit Inference for TTS")

    logger.info("Agent server ready")


def main() -> None:
    """Run the agent application."""
    settings = get_settings()
    setup_logging(settings.log_level)

    logger.info("Starting Real Estate Voice Agent")
    logger.info(f"Company: {settings.company_name}")
    logger.info(f"LiveKit URL: {settings.livekit_url}")

    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
            num_idle_processes=settings.num_idle_processes,
        )
    )


if __name__ == "__main__":
    main()
