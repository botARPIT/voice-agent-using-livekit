"""
Mortgage calculation tools for the voice agent.
"""

from typing import Optional

from livekit.agents import function_tool

from ..services.mortgage import MortgageCalculator


@function_tool
def get_mortgage_estimate(
    property_price: float,
    down_payment_percent: float = 20.0,
    interest_rate: float = 7.0,
    loan_term_years: int = 30
) -> str:
    """
    Calculate estimated monthly mortgage payment.

    Args:
        property_price: The total property price
        down_payment_percent: Down payment percentage (default 20%)
        interest_rate: Annual interest rate in percent (default 7.0)
        loan_term_years: Loan term in years (default 30)

    Returns estimated monthly payment information.
    """
    annual_rate = interest_rate / 100

    result = MortgageCalculator.calculate_payment(
        property_price=property_price,
        down_payment_percent=down_payment_percent,
        annual_rate=annual_rate,
        years=loan_term_years
    )

    return (
        f"Estimated Mortgage Details:\n\n"
        f"Property Price: ${result.price:,.0f}\n"
        f"Down Payment ({down_payment_percent}%): ${result.down_payment:,.0f}\n"
        f"Loan Amount: ${result.loan_amount:,.0f}\n"
        f"Interest Rate: {interest_rate}%\n"
        f"Loan Term: {loan_term_years} years\n\n"
        f"Estimated Monthly Payment: ${result.monthly_payment:,.2f}\n"
        f"Total Interest Over Loan: ${result.total_interest:,.0f}\n\n"
        f"Note: This does not include property taxes, insurance, or HOA fees. "
        f"Actual rates may vary based on credit score and market conditions."
    )


@function_tool
def calculate_affordability(
    monthly_income: float,
    monthly_debts: float = 0,
    down_payment: float = 0,
    interest_rate: float = 7.0,
    loan_term_years: int = 30
) -> str:
    """
    Calculate how much house a buyer can afford.

    Args:
        monthly_income: Gross monthly income
        monthly_debts: Existing monthly debt payments
        down_payment: Available down payment amount
        interest_rate: Annual interest rate in percent (default 7.0)
        loan_term_years: Loan term in years (default 30)

    Returns affordability estimate.
    """
    annual_rate = interest_rate / 100

    result = MortgageCalculator.calculate_affordability(
        monthly_income=monthly_income,
        monthly_debts=monthly_debts,
        down_payment=down_payment,
        annual_rate=annual_rate,
        years=loan_term_years
    )

    return (
        f"Affordability Analysis:\n\n"
        f"Monthly Income: ${result['monthly_income']:,.2f}\n"
        f"Existing Debts: ${result['monthly_debts']:,.2f}/month\n"
        f"Down Payment: ${result['down_payment']:,.0f}\n\n"
        f"Recommended Maximums:\n"
        f"Monthly Housing Payment: ${result['max_monthly_payment']:,.2f}\n"
        f"Maximum Loan Amount: ${result['max_loan_amount']:,.0f}\n"
        f"Maximum Home Price: ${result['max_home_price']:,.0f}\n\n"
        f"This uses the 28/36 rule (28% of income for housing, 36% total debt).\n"
        f"Actual approval depends on credit score, employment history, and other factors."
    )
