"""
Repository pattern for data access.
In production, replace in-memory storage with database.
"""

import random
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from ..models.property import Property
from ..models.appointment import Appointment, AppointmentStatus
from ..models.lead import Lead, LeadStatus


class BaseRepository(ABC):
    """Base repository with common CRUD operations."""

    @abstractmethod
    def get_by_id(self, entity_id: str):
        """Get entity by ID."""
        pass

    @abstractmethod
    def save(self, entity) -> bool:
        """Save entity to storage."""
        pass


class PropertyRepository(BaseRepository):
    """Repository for property operations."""

    def __init__(self):
        self._properties: dict[str, Property] = {}
        self._seed_data()

    def _seed_data(self) -> None:
        """Load sample properties."""
        sample_properties = [
            Property(
                id="prop-001",
                address="123 Main Street",
                city="San Francisco",
                state="CA",
                zip_code="94102",
                price=1250000,
                bedrooms=3,
                bathrooms=2.5,
                sqft=2100,
                property_type="single-family",
                description="Beautiful Victorian home in Noe Valley with modern updates",
                features=["hardwood floors", "updated kitchen", "garden", "parking"],
                available_for="sale"
            ),
            Property(
                id="prop-002",
                address="456 Market Street",
                city="San Francisco",
                state="CA",
                zip_code="94103",
                price=850000,
                bedrooms=2,
                bathrooms=2.0,
                sqft=1450,
                property_type="condo",
                description="Modern downtown condo with city views",
                features=["gym", "concierge", "rooftop deck", "in-unit laundry"],
                available_for="sale"
            ),
            Property(
                id="prop-003",
                address="789 Sunset Blvd",
                city="Los Angeles",
                state="CA",
                zip_code="90026",
                price=4500,
                bedrooms=4,
                bathrooms=3.0,
                sqft=2800,
                property_type="single-family",
                description="Spacious family home in Echo Park with pool",
                features=["pool", "garage", "fireplace", "mountain views"],
                available_for="rent"
            ),
            Property(
                id="prop-004",
                address="321 Ocean Drive",
                city="Miami",
                state="FL",
                zip_code="33139",
                price=2100000,
                bedrooms=2,
                bathrooms=2.5,
                sqft=1800,
                property_type="condo",
                description="Luxury beachfront condo with ocean views",
                features=["ocean view", "balcony", "valet parking", "spa"],
                available_for="sale"
            ),
        ]
        for prop in sample_properties:
            self._properties[prop.id] = prop

    def get_by_id(self, property_id: str) -> Optional[Property]:
        """Get property by ID."""
        return self._properties.get(property_id)

    def save(self, property: Property) -> bool:
        """Save property to storage."""
        self._properties[property.id] = property
        return True

    def search(
        self,
        city: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_bedrooms: Optional[int] = None,
        property_type: Optional[str] = None,
        available_for: Optional[str] = None,
        limit: int = 10
    ) -> list[Property]:
        """Search properties based on criteria."""
        results = [
            prop for prop in self._properties.values()
            if prop.matches_criteria(
                city=city,
                min_price=min_price,
                max_price=max_price,
                min_bedrooms=min_bedrooms,
                property_type=property_type,
                available_for=available_for,
            )
        ]
        return results[:limit]

    def get_all(self) -> list[Property]:
        """Get all properties."""
        return list(self._properties.values())


class AppointmentRepository(BaseRepository):
    """Repository for appointment operations."""

    def __init__(self):
        self._appointments: dict[str, Appointment] = {}

    def get_by_id(self, appointment_id: str) -> Optional[Appointment]:
        """Get appointment by ID."""
        return self._appointments.get(appointment_id)

    def save(self, appointment: Appointment) -> bool:
        """Save appointment to storage."""
        self._appointments[appointment.id] = appointment
        return True

    def get_by_property(self, property_id: str) -> list[Appointment]:
        """Get all appointments for a property."""
        return [
            apt for apt in self._appointments.values()
            if apt.property_id == property_id
        ]

    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> list[Appointment]:
        """Get appointments in date range."""
        return [
            apt for apt in self._appointments.values()
            if start_date <= apt.scheduled_date <= end_date
        ]

    def get_available_slots(self, date: datetime, property_id: str) -> list[str]:
        """Get available viewing time slots for a date."""
        all_slots = [
            "9:00 AM", "10:30 AM", "1:00 PM",
            "2:30 PM", "4:00 PM", "5:30 PM"
        ]

        # Get booked slots
        booked = [
            apt.scheduled_date.strftime("%I:%M %p")
            for apt in self._appointments.values()
            if apt.scheduled_date.date() == date.date()
            and apt.property_id == property_id
            and apt.status not in [AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW]
        ]

        # Filter out booked slots
        available = [slot for slot in all_slots if slot not in booked]

        # Simulate some random bookings
        available = [slot for slot in available if random.random() > 0.2]

        return available


class LeadRepository(BaseRepository):
    """Repository for lead operations."""

    def __init__(self):
        self._leads: dict[str, Lead] = {}
        self._id_counter = 0

    def _generate_id(self) -> str:
        """Generate a unique lead ID."""
        self._id_counter += 1
        return f"lead-{datetime.now().strftime('%Y%m%d')}-{self._id_counter:04d}"

    def get_by_id(self, lead_id: str) -> Optional[Lead]:
        """Get lead by ID."""
        return self._leads.get(lead_id)

    def save(self, lead: Lead) -> bool:
        """Save lead to storage."""
        if not lead.id:
            lead.id = self._generate_id()
        self._leads[lead.id] = lead
        return True

    def get_by_status(self, status: LeadStatus) -> list[Lead]:
        """Get leads by status."""
        return [lead for lead in self._leads.values() if lead.status == status]

    def get_new_leads(self) -> list[Lead]:
        """Get all new leads."""
        return self.get_by_status(LeadStatus.NEW)
