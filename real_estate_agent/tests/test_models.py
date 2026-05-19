"""
Tests for data models.
"""

import pytest
from datetime import datetime

from ..models.property import Property
from ..models.appointment import Appointment, AppointmentStatus
from ..models.lead import Lead, LeadStatus, LeadSource


class TestProperty:
    """Test cases for Property model."""

    def test_create_property(self):
        """Test property creation."""
        prop = Property(
            id="test-001",
            address="123 Test St",
            city="San Francisco",
            state="CA",
            zip_code="94102",
            price=1000000,
            bedrooms=3,
            bathrooms=2.0,
            sqft=1500,
            property_type="condo",
            description="Test property",
            features=["pool", "gym"],
            available_for="sale"
        )

        assert prop.id == "test-001"
        assert prop.price == 1000000
        assert prop.full_address == "123 Test St, San Francisco, CA 94102"
        assert prop.price_formatted == "$1,000,000"

    def test_price_per_sqft(self):
        """Test price per square foot calculation."""
        prop = Property(
            id="test-002",
            address="456 Test Ave",
            city="Test City",
            state="CA",
            zip_code="12345",
            price=1000000,
            bedrooms=2,
            bathrooms=2.0,
            sqft=2000,
            property_type="house",
            description="Test",
        )

        assert prop.price_per_sqft == 500.0

    def test_matches_criteria(self):
        """Test property matching criteria."""
        prop = Property(
            id="test-003",
            address="789 Test Blvd",
            city="Miami",
            state="FL",
            zip_code="33139",
            price=500000,
            bedrooms=2,
            bathrooms=2.0,
            sqft=1000,
            property_type="condo",
            description="Test",
            available_for="sale"
        )

        # Should match
        assert prop.matches_criteria(city="Miami") is True
        assert prop.matches_criteria(min_price=400000) is True
        assert prop.matches_criteria(max_price=600000) is True
        assert prop.matches_criteria(min_bedrooms=2) is True

        # Should not match
        assert prop.matches_criteria(city="New York") is False
        assert prop.matches_criteria(min_price=600000) is False
        assert prop.matches_criteria(max_price=400000) is False
        assert prop.matches_criteria(min_bedrooms=3) is False

    def test_rental_price_formatting(self):
        """Test rental price formatting."""
        prop = Property(
            id="test-004",
            address="321 Test Ln",
            city="Los Angeles",
            state="CA",
            zip_code="90001",
            price=3500,
            bedrooms=1,
            bathrooms=1.0,
            sqft=800,
            property_type="apartment",
            description="Test",
            available_for="rent"
        )

        assert prop.price_formatted == "$3,500/month"

    def test_to_dict(self):
        """Test property serialization."""
        prop = Property(
            id="test-005",
            address="555 Test Dr",
            city="Test",
            state="TX",
            zip_code="75001",
            price=300000,
            bedrooms=3,
            bathrooms=2.5,
            sqft=2000,
            property_type="house",
            description="A great home",
            features=["garage", "yard"],
        )

        data = prop.to_dict()
        assert data["id"] == "test-005"
        assert data["price"] == 300000
        assert data["bedrooms"] == 3
        assert "full_address" in data
        assert "price_formatted" in data


class TestAppointment:
    """Test cases for Appointment model."""

    def test_create_appointment(self):
        """Test appointment creation."""
        apt = Appointment(
            id="apt-001",
            property_id="prop-001",
            client_name="John Doe",
            client_phone="555-1234",
            scheduled_date=datetime.now(),
        )

        assert apt.id == "apt-001"
        assert apt.status == AppointmentStatus.SCHEDULED
        assert apt.client_name == "John Doe"

    def test_confirm_appointment(self):
        """Test confirming an appointment."""
        apt = Appointment(
            id="apt-002",
            property_id="prop-002",
            client_name="Jane Smith",
            client_phone="555-5678",
            scheduled_date=datetime.now(),
        )

        apt.confirm()
        assert apt.status == AppointmentStatus.CONFIRMED

    def test_complete_appointment(self):
        """Test completing an appointment."""
        apt = Appointment(
            id="apt-003",
            property_id="prop-003",
            client_name="Bob Wilson",
            client_phone="555-9999",
            scheduled_date=datetime.now(),
        )

        apt.complete()
        assert apt.status == AppointmentStatus.COMPLETED

    def test_cancel_appointment(self):
        """Test cancelling an appointment."""
        apt = Appointment(
            id="apt-004",
            property_id="prop-004",
            client_name="Alice Brown",
            client_phone="555-0000",
            scheduled_date=datetime.now(),
        )

        apt.cancel()
        assert apt.status == AppointmentStatus.CANCELLED

    def test_to_dict(self):
        """Test appointment serialization."""
        apt = Appointment(
            id="apt-005",
            property_id="prop-005",
            client_name="Test Client",
            client_phone="555-1111",
            scheduled_date=datetime(2024, 1, 15, 14, 30),
            notes="Call before arrival",
        )

        data = apt.to_dict()
        assert data["id"] == "apt-005"
        assert data["client_name"] == "Test Client"
        assert data["status"] == "scheduled"


class TestLead:
    """Test cases for Lead model."""

    def test_create_lead(self):
        """Test lead creation."""
        lead = Lead(
            id="lead-001",
            name="Test Lead",
            phone="555-4444",
            email="test@example.com",
            budget_min=500000,
            budget_max=1000000,
        )

        assert lead.id == "lead-001"
        assert lead.status == LeadStatus.NEW
        assert lead.source == LeadSource.PHONE

    def test_qualify_lead(self):
        """Test qualifying a lead."""
        lead = Lead(
            id="lead-002",
            name="Qualified Lead",
            phone="555-5555",
        )

        lead.qualify()
        assert lead.status == LeadStatus.QUALIFIED

    def test_convert_lead(self):
        """Test converting a lead."""
        lead = Lead(
            id="lead-003",
            name="Converted Lead",
            phone="555-6666",
        )

        lead.convert()
        assert lead.status == LeadStatus.CONVERTED

    def test_mark_contacted(self):
        """Test marking lead as contacted."""
        lead = Lead(
            id="lead-004",
            name="Contacted Lead",
            phone="555-7777",
            status=LeadStatus.NEW,
        )

        lead.mark_contacted()
        assert lead.status == LeadStatus.CONTACTED
        assert lead.last_contact is not None

    def test_to_dict(self):
        """Test lead serialization."""
        lead = Lead(
            id="lead-005",
            name="Dict Test",
            phone="555-8888",
            budget_min=400000,
            budget_max=800000,
            preferred_location="San Francisco",
        )

        data = lead.to_dict()
        assert data["id"] == "lead-005"
        assert data["budget_min"] == 400000
        assert data["status"] == "new"
        assert data["preferred_location"] == "San Francisco"
