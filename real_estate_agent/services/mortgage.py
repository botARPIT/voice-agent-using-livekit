"""
Mortgage calculation utilities.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MortgageResult:
    """Result of mortgage calculation."""
    monthly_payment: float
    total_payment: float
    total_interest: float
    loan_amount: float
    down_payment: float
    price: float


class MortgageCalculator:
    """Calculate mortgage payments and affordability."""

    DEFAULT_RATE = 0.07  # 7% annual interest
    DEFAULT_TERM_YEARS = 30

    @classmethod
    def calculate_payment(
        cls,
        property_price: float,
        down_payment_percent: float = 20.0,
        annual_rate: float = DEFAULT_RATE,
        years: int = DEFAULT_TERM_YEARS
    ) -> MortgageResult:
        """Calculate monthly mortgage payment."""
        down_payment = property_price * (down_payment_percent / 100)
        loan_amount = property_price - down_payment
        monthly_rate = annual_rate / 12
        num_payments = years * 12

        if monthly_rate == 0:
            monthly_payment = loan_amount / num_payments
        else:
            monthly_payment = loan_amount * (
                monthly_rate * (1 + monthly_rate) ** num_payments
            ) / (
                (1 + monthly_rate) ** num_payments - 1
            )

        total_payment = monthly_payment * num_payments
        total_interest = total_payment - loan_amount

        return MortgageResult(
            monthly_payment=monthly_payment,
            total_payment=total_payment,
            total_interest=total_interest,
            loan_amount=loan_amount,
            down_payment=down_payment,
            price=property_price,
        )

    @classmethod
    def calculate_affordability(
        cls,
        monthly_income: float,
        monthly_debts: float = 0,
        down_payment: float = 0,
        annual_rate: float = DEFAULT_RATE,
        years: int = DEFAULT_TERM_YEARS
    ) -> dict:
        """Calculate maximum affordable home price."""
        # 28/36 rule: 28% of income for housing, 36% total debt
        max_housing_payment = monthly_income * 0.28
        max_total_debt = monthly_income * 0.36
        max_mortgage_payment = min(
            max_housing_payment,
            max_total_debt - monthly_debts
        )

        # Calculate max loan amount
        monthly_rate = annual_rate / 12
        num_payments = years * 12

        if monthly_rate == 0:
            max_loan = max_mortgage_payment * num_payments
        else:
            max_loan = max_mortgage_payment * (
                (1 + monthly_rate) ** num_payments - 1
            ) / (
                monthly_rate * (1 + monthly_rate) ** num_payments
            )

        max_home_price = max_loan + down_payment

        return {
            "monthly_income": monthly_income,
            "monthly_debts": monthly_debts,
            "max_monthly_payment": max_mortgage_payment,
            "max_loan_amount": max_loan,
            "max_home_price": max_home_price,
            "down_payment": down_payment,
        }

    @classmethod
    def format_result(cls, result: MortgageResult) -> str:
        """Format mortgage result as readable string."""
        return (
            f"Monthly Payment: ${result.monthly_payment:,.2f}\n"
            f"Down Payment: ${result.down_payment:,.0f}\n"
            f"Loan Amount: ${result.loan_amount:,.0f}\n"
            f"Total Interest: ${result.total_interest:,.0f}"
        )
