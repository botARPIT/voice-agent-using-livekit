"""
Property search agent implementation.
"""

from livekit.agents import Agent, function_tool

from .instructions import AgentInstructions
from ..tools import (
    search_properties,
    get_property_details,
    get_mortgage_estimate,
    calculate_affordability,
    get_market_insights,
    get_neighborhood_info,
    check_availability,
)


class PropertySearchAgent:
    """Property search specialist agent."""

    @staticmethod
    def create() -> Agent:
        """Create the property search agent instance."""
        return Agent(
            instructions=AgentInstructions.PROPERTY_SEARCH,
            tools=[
                search_properties,
                get_property_details,
                get_mortgage_estimate,
                calculate_affordability,
                get_market_insights,
                get_neighborhood_info,
                check_availability,
            ],
        )
