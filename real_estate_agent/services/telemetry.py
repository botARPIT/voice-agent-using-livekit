"""
Telemetry and metrics collection for the voice agent.
Tracks TTFA, TTFT, token usage, interruption rate, and more.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, Callable

from livekit.agents import metrics, AgentStateChangedEvent, MetricsCollectedEvent

logger = logging.getLogger("telemetry")


@dataclass
class SessionMetrics:
    """Metrics for a single session."""
    session_id: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    ttfa_ms: Optional[float] = None  # Time to First Audio
    ttft_ms: Optional[float] = None  # Time to First Token
    total_tokens: int = 0
    interruptions: int = 0
    fallback_activations: int = 0
    tool_calls: int = 0
    tool_latency_ms: float = 0.0
    eou_metrics: Optional[metrics.EOUMetrics] = None
    current_speech_id: Optional[str] = None


class UsageCollector:
    """Collect and aggregate usage metrics across sessions."""

    def __init__(self):
        self._sessions: Dict[str, SessionMetrics] = {}
        self._total_tokens = 0
        self._total_interruptions = 0
        self._total_fallbacks = 0

    def start_session(self, session_id: str) -> SessionMetrics:
        """Start tracking a new session."""
        session = SessionMetrics(session_id=session_id)
        self._sessions[session_id] = session
        logger.info(f"Started metrics collection for session {session_id}")
        return session

    def end_session(self, session_id: str) -> Optional[SessionMetrics]:
        """End tracking a session."""
        session = self._sessions.get(session_id)
        if session:
            session.end_time = datetime.now()
            self._total_tokens += session.total_tokens
            self._total_interruptions += session.interruptions
            self._total_fallbacks += session.fallback_activations
            logger.info(f"Ended metrics collection for session {session_id}")
        return session

    def collect(self, metrics_data: Any) -> None:
        """Collect metrics from a MetricsCollectedEvent."""
        try:
            if hasattr(metrics_data, 'type'):
                if metrics_data.type == "eou_metrics":
                    self._handle_eou_metrics(metrics_data)
                elif metrics_data.type == "token_usage":
                    self._handle_token_usage(metrics_data)
                elif metrics_data.type == "interruption":
                    self._handle_interruption(metrics_data)

            # Log the metrics
            metrics.log_metrics(metrics_data)
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")

    def _handle_eou_metrics(self, eou_metrics: metrics.EOUMetrics) -> None:
        """Handle End of Utterance metrics."""
        logger.info(f"EOU Metrics collected: speech_id={eou_metrics.speech_id}")
        # Store for TTFA calculation
        for session in self._sessions.values():
            session.eou_metrics = eou_metrics

    def _handle_token_usage(self, token_metrics: Any) -> None:
        """Handle token usage metrics."""
        if hasattr(token_metrics, 'tokens'):
            for session in self._sessions.values():
                session.total_tokens += token_metrics.tokens

    def _handle_interruption(self, interruption_metrics: Any) -> None:
        """Handle interruption metrics."""
        for session in self._sessions.values():
            session.interruptions += 1
        logger.info("Interruption recorded")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all collected metrics."""
        total_sessions = len(self._sessions)
        avg_ttfa = None
        avg_ttft = None

        ttfa_values = [s.ttfa_ms for s in self._sessions.values() if s.ttfa_ms]
        ttft_values = [s.ttft_ms for s in self._sessions.values() if s.ttft_ms]

        if ttfa_values:
            avg_ttfa = sum(ttfa_values) / len(ttfa_values)
        if ttft_values:
            avg_ttft = sum(ttft_values) / len(ttft_values)

        return {
            "total_sessions": total_sessions,
            "total_tokens": self._total_tokens,
            "total_interruptions": self._total_interruptions,
            "total_fallbacks": self._total_fallbacks,
            "avg_ttfa_ms": avg_ttfa,
            "avg_ttft_ms": avg_ttft,
        }

    def get_session_metrics(self, session_id: str) -> Optional[SessionMetrics]:
        """Get metrics for a specific session."""
        return self._sessions.get(session_id)


class TelemetryCollector:
    """Main telemetry collector that wires up event handlers."""

    def __init__(self, usage_collector: UsageCollector):
        self.usage_collector = usage_collector
        self.last_eou_metrics: Optional[metrics.EOUMetrics] = None
        self._state_change_handler: Optional[Callable] = None
        self._metrics_handler: Optional[Callable] = None

    def setup_handlers(self, session) -> None:
        """Set up event handlers for a session."""

        @session.on("metrics_collected")
        def _on_metrics_collected(ev: MetricsCollectedEvent):
            """Handle collected metrics."""
            if hasattr(ev.metrics, 'type') and ev.metrics.type == "eou_metrics":
                self.last_eou_metrics = ev.metrics

            self.usage_collector.collect(ev.metrics)

        @session.on("agent_state_changed")
        def _on_agent_state_changed(ev: AgentStateChangedEvent):
            """Track time to first audio when agent starts speaking."""
            if ev.new_state == "speaking" and self.last_eou_metrics:
                # Calculate TTFA
                delta = ev.created_at - self.last_eou_metrics.last_speaking_time
                ttfa_ms = delta.total_seconds() * 1000

                logger.info(f"Time to first audio frame: {ttfa_ms:.0f}ms")

                # Update session metrics
                for session_metrics in self.usage_collector._sessions.values():
                    session_metrics.ttfa_ms = ttfa_ms

        self._state_change_handler = _on_agent_state_changed
        self._metrics_handler = _on_metrics_collected

        logger.info("Telemetry handlers configured")

    def log_usage_summary(self) -> None:
        """Log usage summary."""
        summary = self.usage_collector.get_summary()
        logger.info("=" * 50)
        logger.info("Usage Summary:")
        logger.info(f"  Total Sessions: {summary['total_sessions']}")
        logger.info(f"  Total Tokens: {summary['total_tokens']}")
        logger.info(f"  Total Interruptions: {summary['total_interruptions']}")
        logger.info(f"  Total Fallbacks: {summary['total_fallbacks']}")
        if summary['avg_ttfa_ms']:
            logger.info(f"  Avg TTFA: {summary['avg_ttfa_ms']:.0f}ms")
        if summary['avg_ttft_ms']:
            logger.info(f"  Avg TTFT: {summary['avg_ttft_ms']:.0f}ms")
        logger.info("=" * 50)


def create_telemetry_collector() -> TelemetryCollector:
    """Factory function to create a telemetry collector."""
    usage_collector = UsageCollector()
    return TelemetryCollector(usage_collector)
