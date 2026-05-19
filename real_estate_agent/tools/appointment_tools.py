"""
Appointment scheduling tools for the voice agent.
"""

from datetime import datetime
from typing import Optional

from livekit.agents import function_tool

from ..models.appointment import Appointment, AppointmentStatus
from ..services.repositories import AppointmentRepository, PropertyRepository


# Repository instances
_appointment_repo = AppointmentRepository()
_property_repo = PropertyRepository()


def get_appointment_repository() -> AppointmentRepository:
    """Get the appointment repository instance."""
    return _appointment_repo


def get_property_repository() -> PropertyRepository:
    """Get the property repository instance."""
    return _property_repo


@function_tool
def schedule_viewing(
    property_id: str,
    client_name: str,
    client_phone: str,
    preferred_date: str,
    preferred_time: str,
    notes: str = ""
) -> str:
    """
    Schedule a property viewing appointment.

    Args:
        property_id: The property ID to view
        client_name: Full name of the client
        client_phone: Phone number for contact
        preferred_date: Date in format YYYY-MM-DD
        preferred_time: Time in format HH:MM (24-hour)
        notes: Any special requests or notes

    Returns confirmation of the scheduled appointment.
    """
    prop_repo = get_property_repository()
    prop = prop_repo.get_by_id(property_id)

    if not prop:
        return f"Property with ID '{property_id}' not found. Please check the ID."

    try:
        # Parse datetime
        datetime_str = f"{preferred_date} {preferred_time}"
        scheduled_dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")

        # Check if slot is available
        apt_repo = get_appointment_repository()
        available = apt_repo.get_available_slots(scheduled_dt, property_id)

        # Format time for comparison
        time_str = scheduled_dt.strftime("%I:%M %p").lstrip("0")
        if time_str not in available:
            return (
                f"That time slot is not available. "
                f"Available times for {preferred_date}: {', '.join(available)}"
            )

        # Create appointment
        appointment = Appointment(
            id=f"apt-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            property_id=property_id,
            client_name=client_name,
            client_phone=client_phone,
            scheduled_date=scheduled_dt,
            notes=notes,
            status=AppointmentStatus.SCHEDULED
        )

        apt_repo.save(appointment)

        return (
            f"Perfect! Your viewing has been scheduled.\n\n"
            f"Appointment ID: {appointment.id}\n"
            f"Property: {prop.address}\n"
            f"Date: {scheduled_dt.strftime('%A, %B %d, %Y')}\n"
            f"Time: {scheduled_dt.strftime('%I:%M %p')}\n"
            f"\nWe'll send a confirmation to {client_phone}.\n"
            f"Please arrive 5 minutes early. Looking forward to seeing you!"
        )
    except ValueError as e:
        return f"Invalid date or time format. Please use YYYY-MM-DD for date and HH:MM for time."


@function_tool
def cancel_appointment(appointment_id: str, reason: str = "") -> str:
    """
    Cancel an existing appointment.

    Args:
        appointment_id: The appointment ID to cancel
        reason: Optional reason for cancellation

    Returns confirmation of cancellation.
    """
    apt_repo = get_appointment_repository()
    appointment = apt_repo.get_by_id(appointment_id)

    if not appointment:
        return f"Appointment with ID '{appointment_id}' not found."

    appointment.cancel()
    apt_repo.save(appointment)

    return (
        f"Appointment {appointment_id} has been cancelled. "
        f"{'Reason: ' + reason if reason else ''}\n"
        f"Would you like to reschedule for another time?"
    )
