"""
Greeter agent implementation.
"""

from livekit.agents import Agent, AgentHandoff, function_tool

from .instructions import AgentInstructions
from ..tools import (
    search_properties,
    get_property_details,
    schedule_viewing,
    get_mortgage_estimate,
    calculate_affordability,
    get_market_insights,
    get_neighborhood_info,
)


class GreeterAgent:
    """Greeter agent that routes callers to appropriate specialists."""

    @staticmethod
    def create() -> Agent:
        """Create the greeter agent instance."""
        return Agent(
            instructions=AgentInstructions.GREETER,
            tools=[
                GreeterAgent._transfer_to_property_search,
                GreeterAgent._transfer_to_scheduling,
                GreeterAgent._transfer_to_human,
            ],
        )

    @staticmethod
    @function_tool
    def _transfer_to_property_search() -> AgentHandoff:
        """Transfer the caller to the property search specialist."""
        from .property_search import PropertySearchAgent

        return AgentHandoff(
            agent=PropertySearchAgent.create(),
            handoff_instructions="The caller is looking for properties. Help them find suitable options."
        )

    @staticmethod
    @function_tool
    def _transfer_to_scheduling(property_id: str = "") -> AgentHandoff:
        """Transfer the caller to the scheduling coordinator."""
        from .scheduling import SchedulingAgent

        instructions = "Help the caller schedule a property viewing."
        if property_id:
            instructions += f" They are interested in property {property_id}."

        return AgentHandoff(
            agent=SchedulingAgent.create(),
            handoff_instructions=instructions
        )

    @staticmethod
    @function_tool
    def _transfer_to_human(reason: str = "") -> str:
        """Transfer the caller to a human agent."""
        return (
            "I'll connect you with one of our licensed agents right away. "
            "Please hold while I transfer your call.\n"
            f"Transfer reason: {reason if reason else 'General assistance'}"
        )
