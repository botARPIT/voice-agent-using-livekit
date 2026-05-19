"""
Tests for service layer.
"""

import pytest
from datetime import datetime

from ..services.mortgage import MortgageCalculator
from ..services.repositories import PropertyRepository, AppointmentRepository, LeadRepository
from ..services.market_data import MarketDataService


class TestMortgageCalculator:
    """Test cases for MortgageCalculator."""

    def test_calculate_payment(self):
        """Test mortgage payment calculation."""
        result = MortgageCalculator.calculate_payment(
            property_price=500000,
            down_payment_percent=20.0,
            annual_rate=0.07,
            years=30
        )

        assert result.down_payment == 100000
        assert result.loan_amount == 400000
        assert result.monthly_payment > 0
        assert result.total_payment > result.loan_amount

    def test_calculate_affordability(self):
        """Test affordability calculation."""
        result = MortgageCalculator.calculate_affordability(
            monthly_income=10000,
            monthly_debts=2000,
            down_payment=50000,
            annual_rate=0.07,
            years=30
        )

        assert result["monthly_income"] == 10000
        assert result["max_monthly_payment"] <= 2800  # 28% rule
        assert result["max_home_price"] > 0


class TestPropertyRepository:
    """Test cases for PropertyRepository."""

    def test_get_by_id_existing(self):
        """Test getting existing property."""
        repo = PropertyRepository()
        prop = repo.get_by_id("prop-001")

        assert prop is not None
        assert prop.id == "prop-001"
        assert prop.city == "San Francisco"

    def test_get_by_id_nonexistent(self):
        """Test getting non-existent property."""
        repo = PropertyRepository()
        prop = repo.get_by_id("nonexistent")

        assert prop is None

    def test_search_by_city(self):
        """Test searching by city."""
        repo = PropertyRepository()
        results = repo.search(city="San Francisco")

        assert len(results) > 0
        assert all("San Francisco" in r.city for r in results)

    def test_search_by_price_range(self):
        """Test searching by price range."""
        repo = PropertyRepository()
        results = repo.search(min_price=1000000, max_price=2000000)

        assert len(results) > 0
        assert all(1000000 <= r.price <= 2000000 for r in results)

    def test_search_by_bedrooms(self):
        """Test searching by bedroom count."""
        repo = PropertyRepository()
        results = repo.search(min_bedrooms=3)

        assert len(results) > 0
        assert all(r.bedrooms >= 3 for r in results)

    def test_search_no_results(self):
        """Test search with no matches."""
        repo = PropertyRepository()
        results = repo.search(city="Nonexistent City")

        assert len(results) == 0


class TestAppointmentRepository:
    """Test cases for AppointmentRepository."""

    def test_save_and_get(self):
        """Test saving and retrieving appointment."""
        repo = AppointmentRepository()

        from ..models.appointment import Appointment
        apt = Appointment(
            id="apt-test-001",
            property_id="prop-001",
            client_name="Test Client",
            client_phone="555-0000",
            scheduled_date=datetime.now(),
        )

        repo.save(apt)
        retrieved = repo.get_by_id("apt-test-001")

        assert retrieved is not None
        assert retrieved.client_name == "Test Client"

    def test_get_by_property(self):
        """Test getting appointments by property."""
        repo = AppointmentRepository()
        from ..models.appointment import Appointment

        apt1 = Appointment(
            id="apt-test-002",
            property_id="prop-001",
            client_name="Client 1",
            client_phone="555-0001",
            scheduled_date=datetime.now(),
        )
        apt2 = Appointment(
            id="apt-test-003",
            property_id="prop-001",
            client_name="Client 2",
            client_phone="555-0002",
            scheduled_date=datetime.now(),
        )

        repo.save(apt1)
        repo.save(apt2)

        results = repo.get_by_property("prop-001")
        assert len(results) >= 2


class TestMarketDataService:
    """Test cases for MarketDataService."""

    def test_get_market_data_existing(self):
        """Test getting market data for known city."""
        data = MarketDataService.get_market_data("San Francisco")

        assert data is not None
        assert data.city == "San Francisco"
        assert data.median_price > 0

    def test_get_market_data_nonexistent(self):
        """Test getting market data for unknown city."""
        data = MarketDataService.get_market_data("Unknown City")

        assert data is None

    def test_get_neighborhood_info_existing(self):
        """Test getting neighborhood info."""
        info = MarketDataService.get_neighborhood_info("noe valley", "san francisco")

        assert info is not None
        assert "vibe" in info
        assert "price_range" in info

    def test_get_neighborhood_info_nonexistent(self):
        """Test getting neighborhood info for unknown area."""
        info = MarketDataService.get_neighborhood_info("unknown", "city")

        assert info is None

    def test_format_market_summary(self):
        """Test market summary formatting."""
        data = MarketDataService.get_market_data("Miami")
        summary = MarketDataService.format_market_summary(data)

        assert "Miami" in summary
        assert "Median Price" in summary
        assert "$" in summary
