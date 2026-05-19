"""
Langfuse integration for tracing and observability.
"""

import os
import base64
import logging
from typing import Optional

from livekit.agents.telemetry import set_tracer_provider

logger = logging.getLogger("langfuse")


def setup_langfuse(
    host: Optional[str] = None,
    public_key: Optional[str] = None,
    secret_key: Optional[str] = None,
) -> bool:
    """
    Setup Langfuse tracing with OpenTelemetry.

    Args:
        host: Langfuse host URL
        public_key: Langfuse public key
        secret_key: Langfuse secret key

    Returns:
        True if setup successful, False otherwise
    """
    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        # Get credentials from environment or parameters
        public_key = public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = secret_key or os.getenv("LANGFUSE_SECRET_KEY")
        host = host or os.getenv("LANGFUSE_HOST", "https://us.cloud.langfuse.com")

        if not public_key or not secret_key:
            logger.warning("Langfuse credentials not found. Tracing disabled.")
            return False

        # Create authentication header
        auth = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()

        # Set environment variables for OTLP
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = f"{host.rstrip('/')}/api/public/otel"
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {auth}"

        # Create tracer provider
        provider = TracerProvider()
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
        set_tracer_provider(provider)

        logger.info(f"Langfuse tracing configured for project at {host}")
        return True

    except ImportError as e:
        logger.warning(f"OpenTelemetry dependencies not installed: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to setup Langfuse: {e}")
        return False


def get_langfuse_client():
    """Get Langfuse client if available."""
    try:
        from langfuse import Langfuse
        return Langfuse()
    except Exception as e:
        logger.debug(f"Langfuse client not available: {e}")
        return None
