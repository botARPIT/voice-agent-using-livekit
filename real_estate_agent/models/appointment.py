"""
Appointment data model for property viewings.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class AppointmentStatus(Enum):
    """Status of an appointment."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


@dataclass
class Appointment:
    """Represents a property viewing appointment."""

    id: str
    property_id: str
    client_name: str
    client_phone: str
    client_email: Optional[str] = None
    scheduled_date: datetime = field(default_factory=datetime.now)
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    agent_id: Optional[str] = None
    reminder_sent: bool = False

    def confirm(self) -> None:
        """Mark appointment as confirmed."""
        self.status = AppointmentStatus.CONFIRMED

    def complete(self) -> None:
        """Mark appointment as completed."""
        self.status = AppointmentStatus.COMPLETED

    def cancel(self) -> None:
        """Mark appointment as cancelled."""
        self.status = AppointmentStatus.CANCELLED

    def to_dict(self) -> dict:
        """Convert appointment to dictionary."""
        return {
            "id": self.id,
            "property_id": self.property_id,
            "client_name": self.client_name,
            "client_phone": self.client_phone,
            "client_email": self.client_email,
            "scheduled_date": self.scheduled_date.isoformat(),
            "status": self.status.value,
            "notes": self.notes,
            "reminder_sent": self.reminder_sent,
        }
