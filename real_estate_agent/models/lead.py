"""
Lead data model for potential clients.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class LeadStatus(Enum):
    """Status of a lead."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    VIEWING_SCHEDULED = "viewing_scheduled"
    CONVERTED = "converted"
    LOST = "lost"


class LeadSource(Enum):
    """Source of the lead."""
    PHONE = "phone"
    WEBSITE = "website"
    REFERRAL = "referral"
    WALK_IN = "walk_in"
    SOCIAL_MEDIA = "social_media"
    OTHER = "other"


@dataclass
class Lead:
    """Represents a potential client lead."""

    id: str
    name: str
    phone: str
    email: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    preferred_location: Optional[str] = None
    property_type_preference: Optional[str] = None
    bedrooms_min: Optional[int] = None
    status: LeadStatus = LeadStatus.NEW
    source: LeadSource = LeadSource.PHONE
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    agent_id: Optional[str] = None
    last_contact: Optional[datetime] = None

    def qualify(self) -> None:
        """Mark lead as qualified."""
        self.status = LeadStatus.QUALIFIED
        self.updated_at = datetime.now()

    def convert(self) -> None:
        """Mark lead as converted."""
        self.status = LeadStatus.CONVERTED
        self.updated_at = datetime.now()

    def mark_contacted(self) -> None:
        """Update last contact time."""
        self.last_contact = datetime.now()
        if self.status == LeadStatus.NEW:
            self.status = LeadStatus.CONTACTED

    def to_dict(self) -> dict:
        """Convert lead to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "budget_min": self.budget_min,
            "budget_max": self.budget_max,
            "preferred_location": self.preferred_location,
            "property_type_preference": self.property_type_preference,
            "bedrooms_min": self.bedrooms_min,
            "status": self.status.value,
            "source": self.source.value,
            "notes": self.notes,
        }
