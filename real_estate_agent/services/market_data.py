"""
Market data service for neighborhood insights and pricing.
"""

from typing import Optional


class MarketData:
    """Market data for a specific location."""

    def __init__(
        self,
        city: str,
        median_price: float,
        price_per_sqft: float,
        inventory: str,
        trend: str,
        days_on_market: int,
        property_types: Optional[dict] = None
    ):
        self.city = city
        self.median_price = median_price
        self.price_per_sqft = price_per_sqft
        self.inventory = inventory
        self.trend = trend
        self.days_on_market = days_on_market
        self.property_types = property_types or {}


class MarketDataService:
    """Service for retrieving market data."""

    # Mock market data (replace with API in production)
    _market_data = {
        "san francisco": MarketData(
            city="San Francisco",
            median_price=1450000,
            price_per_sqft=1100,
            inventory="Low",
            trend="Prices up 3% YoY",
            days_on_market=18,
            property_types={
                "condo": {"median": 1200000, "price_per_sqft": 1050},
                "single-family": {"median": 1850000, "price_per_sqft": 1250},
            }
        ),
        "los angeles": MarketData(
            city="Los Angeles",
            median_price=950000,
            price_per_sqft=650,
            inventory="Moderate",
            trend="Stable",
            days_on_market=28,
            property_types={
                "condo": {"median": 750000, "price_per_sqft": 580},
                "single-family": {"median": 1100000, "price_per_sqft": 720},
            }
        ),
        "miami": MarketData(
            city="Miami",
            median_price=580000,
            price_per_sqft=420,
            inventory="High",
            trend="Prices up 5% YoY",
            days_on_market=45,
            property_types={
                "condo": {"median": 450000, "price_per_sqft": 380},
                "single-family": {"median": 750000, "price_per_sqft": 480},
            }
        ),
        "new york": MarketData(
            city="New York",
            median_price=785000,
            price_per_sqft=890,
            inventory="Low",
            trend="Prices up 2% YoY",
            days_on_market=65,
            property_types={
                "condo": {"median": 900000, "price_per_sqft": 950},
                "single-family": {"median": 650000, "price_per_sqft": 750},
            }
        ),
    }

    _neighborhoods = {
        ("noe valley", "san francisco"): {
            "vibe": "Family-friendly, charming Victorian homes",
            "price_range": "$1.2M - $3M",
            "schools": "Highly rated",
            "transit": "J-Church Muni line, good bus connections",
            "highlights": ["24th Street shopping", "Saturday farmer's market", "Parks"]
        },
        ("echo park", "los angeles"): {
            "vibe": "Trendy, artistic community",
            "price_range": "$800K - $1.8M",
            "schools": "Mixed ratings",
            "transit": "Limited Metro, car-dependent",
            "highlights": ["Echo Park Lake", "Sunset Boulevard nightlife", "Art scene"]
        },
        ("south beach", "miami"): {
            "vibe": "Vibrant, beachfront living",
            "price_range": "$500K - $2M+",
            "schools": "Good options nearby",
            "transit": "Free trolley, walkable",
            "highlights": ["Ocean Drive", "Art Deco district", "Nightlife"]
        },
        ("brooklyn heights", "new york"): {
            "vibe": "Historic, family-oriented",
            "price_range": "$1.5M - $5M",
            "schools": "Excellent public schools",
            "transit": "Multiple subway lines",
            "highlights": ["Promenade views", "Historic brownstones", "Waterfront"]
        },
    }

    @classmethod
    def get_market_data(cls, city: str) -> Optional[MarketData]:
        """Get market data for a city."""
        return cls._market_data.get(city.lower())

    @classmethod
    def get_neighborhood_info(cls, neighborhood: str, city: str) -> Optional[dict]:
        """Get information about a specific neighborhood."""
        key = (neighborhood.lower(), city.lower())
        return cls._neighborhoods.get(key)

    @classmethod
    def format_market_summary(cls, data: MarketData, property_type: str = "") -> str:
        """Format market data as readable summary."""
        result = [
            f"Market Insights for {data.city}:",
            f"Median Price: ${data.median_price:,.0f}",
            f"Price per Sq Ft: ${data.price_per_sqft}",
            f"Inventory Level: {data.inventory}",
            f"Trend: {data.trend}",
            f"Average Days on Market: {data.days_on_market}",
        ]

        if property_type and property_type.lower() in data.property_types:
            pt_data = data.property_types[property_type.lower()]
            result.append(
                f"{property_type.title()} Median: ${pt_data['median']:,.0f} "
                f"(${pt_data['price_per_sqft']}/sqft)"
            )

        return "\n".join(result)

    @classmethod
    def format_neighborhood_info(cls, neighborhood: str, city: str, info: dict) -> str:
        """Format neighborhood info as readable string."""
        return (
            f"About {neighborhood.title()}, {city.title()}:\n"
            f"Vibe: {info['vibe']}\n"
            f"Price Range: {info['price_range']}\n"
            f"Schools: {info['schools']}\n"
            f"Transit: {info['transit']}\n"
            f"Highlights: {', '.join(info['highlights'])}"
        )
