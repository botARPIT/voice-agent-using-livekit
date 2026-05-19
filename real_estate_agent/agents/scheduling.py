"""
Scheduling agent implementation.
"""

from livekit.agents import Agent, function_tool

from .instructions import AgentInstructions
from ..tools import (
    schedule_viewing,
    check_availability,
    get_property_details,
    cancel_appointment,
)


class SchedulingAgent:
    """Scheduling coordinator agent."""

    @staticmethod
    def create() -> Agent:
        """Create the scheduling agent instance."""
        return Agent(
            instructions=AgentInstructions.SCHEDULING,
            tools=[
                schedule_viewing,
                check_availability,
                get_property_details,
                cancel_appointment,
            ],
        )
