"""
Agent builder for creating agent instances.
"""

from livekit.agents import Agent

from .greeter import GreeterAgent
from .property_search import PropertySearchAgent
from .scheduling import SchedulingAgent


class AgentBuilder:
    """Builder for creating agent instances."""

    @staticmethod
    def get_default_agent() -> Agent:
        """Get the default (greeter) agent."""
        return GreeterAgent.create()

    @staticmethod
    def get_agent_by_name(name: str) -> Agent:
        """Get an agent by name.

        Args:
            name: Agent name (greeter, property_search, scheduling)

        Returns:
            Agent instance

        Raises:
            ValueError: If agent name not found
        """
        name = name.lower()

        if name in ["greeter", "default"]:
            return GreeterAgent.create()
        elif name in ["property_search", "property", "search"]:
            return PropertySearchAgent.create()
        elif name in ["scheduling", "scheduler", "schedule"]:
            return SchedulingAgent.create()
        else:
            raise ValueError(f"Unknown agent name: {name}")
