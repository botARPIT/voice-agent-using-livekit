"""
Market data and neighborhood information tools.
"""

from typing import Optional

from livekit.agents import function_tool

from ..services.market_data import MarketDataService


@function_tool
def get_market_insights(city: str, property_type: str = "") -> str:
    """
    Get current market insights for a location.

    Args:
        city: City name
        property_type: Type of property (optional)

    Returns market insights and trends.
    """
    data = MarketDataService.get_market_data(city)

    if not data:
        return (
            f"I don't have specific market data for {city.title()}. "
            f"Please contact one of our agents for detailed market insights."
        )

    return (
        MarketDataService.format_market_summary(data, property_type) +
        "\n\nWould you like me to search for properties in this market?"
    )


@function_tool
def get_neighborhood_info(neighborhood: str, city: str) -> str:
    """
    Get information about a specific neighborhood.

    Args:
        neighborhood: Neighborhood name
        city: City name

    Returns neighborhood details.
    """
    info = MarketDataService.get_neighborhood_info(neighborhood, city)

    if not info:
        return (
            f"I don't have detailed information about {neighborhood} in {city.title()}. "
            f"I'd recommend speaking with one of our local agents who can provide "
            f"comprehensive neighborhood insights."
        )

    return (
        MarketDataService.format_neighborhood_info(neighborhood, city, info) +
        "\n\nWould you like to see properties in this neighborhood?"
    )
