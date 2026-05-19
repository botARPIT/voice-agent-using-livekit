"""
Property search and information tools for the voice agent.
"""

from datetime import datetime
from typing import Optional

from livekit.agents import function_tool

from ..services.repositories import PropertyRepository, AppointmentRepository


# Repository instances (singleton pattern)
_property_repo = PropertyRepository()
_appointment_repo = AppointmentRepository()


def get_property_repository() -> PropertyRepository:
    """Get the property repository instance."""
    return _property_repo


def get_appointment_repository() -> AppointmentRepository:
    """Get the appointment repository instance."""
    return _appointment_repo


@function_tool
def search_properties(
    city: str = "",
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_bedrooms: Optional[int] = None,
    property_type: str = "",
    available_for: str = ""
) -> str:
    """
    Search for properties based on criteria.

    Args:
        city: City name to search in
        min_price: Minimum price in dollars
        max_price: Maximum price in dollars
        min_bedrooms: Minimum number of bedrooms
        property_type: Type of property (house, condo, townhouse, etc.)
        available_for: 'sale', 'rent', or leave empty for both

    Returns a formatted list of matching properties.
    """
    repo = get_property_repository()

    # Convert empty strings to None
    city = city if city else None
    property_type = property_type if property_type else None
    available_for = available_for if available_for else None

    results = repo.search(
        city=city,
        min_price=min_price,
        max_price=max_price,
        min_bedrooms=min_bedrooms,
        property_type=property_type,
        available_for=available_for,
        limit=5
    )

    if not results:
        return "No properties found matching your criteria. Try adjusting your search parameters."

    formatted = []
    for i, prop in enumerate(results, 1):
        formatted.append(
            f"\n{i}. {prop.full_address}\n"
            f"   Price: {prop.price_formatted}\n"
            f"   {prop.bedrooms} bed, {prop.bathrooms} bath, {prop.sqft:,} sqft\n"
            f"   Type: {prop.property_type.title()}\n"
            f"   Features: {', '.join(prop.features[:3])}\n"
            f"   Property ID: {prop.id}"
        )

    return "Here are the properties I found:" + "".join(formatted)


@function_tool
def get_property_details(property_id: str) -> str:
    """
    Get detailed information about a specific property.

    Args:
        property_id: The unique property identifier

    Returns detailed property information.
    """
    repo = get_property_repository()
    prop = repo.get_by_id(property_id)

    if not prop:
        return f"Property with ID '{property_id}' not found. Please check the ID and try again."

    price_per_sqft = prop.price_per_sqft
    price_per_sqft_str = f"${price_per_sqft:.0f}/sqft" if price_per_sqft else "N/A"

    return (
        f"Property Details for {property_id}:\n\n"
        f"Address: {prop.full_address}\n"
        f"Price: {prop.price_formatted}\n"
        f"Price per Sq Ft: {price_per_sqft_str}\n"
        f"Bedrooms: {prop.bedrooms}\n"
        f"Bathrooms: {prop.bathrooms}\n"
        f"Square Feet: {prop.sqft:,}\n"
        f"Type: {prop.property_type.title()}\n"
        f"Available For: {prop.available_for.title()}\n"
        f"\nDescription:\n{prop.description}\n"
        f"\nFeatures:\n- " + "\n- ".join(prop.features)
    )


@function_tool
def check_availability(property_id: str, date: str) -> str:
    """
    Check available viewing times for a property.

    Args:
        property_id: Property ID
        date: Date to check (YYYY-MM-DD)

    Returns available time slots.
    """
    # Validate property exists
    prop_repo = get_property_repository()
    prop = prop_repo.get_by_id(property_id)

    if not prop:
        return f"Property with ID '{property_id}' not found."

    try:
        check_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD format."

    apt_repo = get_appointment_repository()
    available = apt_repo.get_available_slots(check_date, property_id)

    if not available:
        return (
            f"Unfortunately, there are no available slots on {date} for this property. "
            f"Would you like to check another date?"
        )

    slots_str = ", ".join(available)
    return (
        f"Available viewing times for {date} at {prop.address}:\n"
        f"{slots_str}\n\n"
        f"Which time works best for you?"
    )
