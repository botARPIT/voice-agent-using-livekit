"""
Property data model for real estate listings.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Property:
    """Represents a real estate property listing."""

    id: str
    address: str
    city: str
    state: str
    zip_code: str
    price: float
    bedrooms: int
    bathrooms: float
    sqft: int
    property_type: str  # house, condo, townhouse, etc.
    description: str
    features: list[str] = field(default_factory=list)
    available_for: str = "sale"  # sale, rent, both
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    agent_id: Optional[str] = None
    images: list[str] = field(default_factory=list)

    @property
    def full_address(self) -> str:
        """Return the full formatted address."""
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}"

    @property
    def price_formatted(self) -> str:
        """Return formatted price string."""
        if self.available_for == "rent":
            return f"${self.price:,.0f}/month"
        return f"${self.price:,.0f}"

    @property
    def price_per_sqft(self) -> Optional[float]:
        """Calculate price per square foot."""
        if self.sqft > 0:
            return self.price / self.sqft
        return None

    def to_dict(self) -> dict:
        """Convert property to dictionary."""
        return {
            "id": self.id,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "price": self.price,
            "price_formatted": self.price_formatted,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "sqft": self.sqft,
            "property_type": self.property_type,
            "description": self.description,
            "features": self.features,
            "available_for": self.available_for,
            "full_address": self.full_address,
        }

    def matches_criteria(
        self,
        city: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_bedrooms: Optional[int] = None,
        property_type: Optional[str] = None,
        available_for: Optional[str] = None,
    ) -> bool:
        """Check if property matches search criteria."""
        if city and city.lower() not in self.city.lower():
            return False
        if min_price is not None and self.price < min_price:
            return False
        if max_price is not None and self.price > max_price:
            return False
        if min_bedrooms is not None and self.bedrooms < min_bedrooms:
            return False
        if property_type and property_type.lower() not in self.property_type.lower():
            return False
        if available_for and self.available_for != available_for:
            return False
        return True
