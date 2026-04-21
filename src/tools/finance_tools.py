"""
Finance Tools — FinSage
All tools return strings. None raise exceptions — errors returned as strings.
"""

import re
import math
from datetime import datetime


# ─────────────────────────────────────────────
# 1. SIP Maturity Calculator
# ─────────────────────────────────────────────
def calculate_sip(monthly_amount: float, annual_rate: float, years: int) -> str:
    try:
        r = annual_rate / 12 / 100
        n = years * 12
        if r == 0:
            maturity = monthly_amount * n
        else:
            maturity = monthly_amount * (((1 + r) ** n - 1) / r) * (1 + r)
        invested = monthly_amount * n
        returns = maturity - invested
        return (
            f"SIP Calculation:\n"
            f"  Monthly Investment : ₹{monthly_amount:,.0f}\n"
            f"  Annual Rate        : {annual_rate}%\n"
            f"  Duration           : {years} years ({n} months)\n"
            f"  Total Invested     : ₹{invested:,.0f}\n"
            f"  Estimated Returns  : ₹{returns:,.0f}\n"
            f"  Maturity Amount    : ₹{maturity:,.0f}"
        )
    except Exception as e:
        return f"SIP calculation error: {str(e)}"


# ─────────────────────────────────────────────
# 2. EMI Calculator
# ─────────────────────────────────────────────
def calculate_emi(principal: float, annual_rate: float, tenure_years: int) -> str:
    try:
        r = annual_rate / 12 / 100
        n = tenure_years * 12
        if r == 0:
            emi = principal / n
        else:
            emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
        total_payment = emi * n
        total_interest = total_payment - principal
        return (
            f"EMI Calculation:\n"
            f"  Loan Amount        : ₹{principal:,.0f}\n"
            f"  Annual Interest    : {annual_rate}%\n"
            f"  Tenure             : {tenure_years} years ({n} months)\n"
            f"  Monthly EMI        : ₹{emi:,.0f}\n"
            f"  Total Payment      : ₹{total_payment:,.0f}\n"
            f"  Total Interest     : ₹{total_interest:,.0f}"
        )
    except Exception as e:
        return f"EMI calculation error: {str(e)}"


# ─────────────────────────────────────────────
# 3. Compound Interest Calculator
# ─────────────────────────────────────────────
def calculate_compound_interest(
    principal: float, annual_rate: float, years: int, frequency: int = 1
) -> str:
    """frequency: 1=annual, 2=semi-annual, 4=quarterly, 12=monthly"""
    try:
        amount = principal * (1 + annual_rate / 100 / frequency) ** (frequency * years)
        interest = amount - principal
        return (
            f"Compound Interest:\n"
            f"  Principal          : ₹{principal:,.0f}\n"
            f"  Annual Rate        : {annual_rate}%\n"
            f"  Duration           : {years} years\n"
            f"  Compounding        : {frequency}x/year\n"
            f"  Interest Earned    : ₹{interest:,.0f}\n"
            f"  Final Amount       : ₹{amount:,.0f}"
        )
    except Exception as e:
        return f"Compound interest error: {str(e)}"


# ─────────────────────────────────────────────
# 4. Income Tax Estimator (New Regime 2024-25)
# ─────────────────────────────────────────────
def estimate_tax(annual_income: float) -> str:
    try:
        standard_deduction = 75000
        taxable = max(0, annual_income - standard_deduction)

        slabs = [
            (300000, 0.00),
            (400000, 0.05),
            (300000, 0.10),
            (200000, 0.15),
            (300000, 0.20),
            (float("inf"), 0.30),
        ]

        tax = 0.0
        remaining = taxable
        breakdown = []
        for limit, rate in slabs:
            if remaining <= 0:
                break
            chunk = min(remaining, limit)
            slab_tax = chunk * rate
            tax += slab_tax
            if chunk > 0:
                breakdown.append(f"  ₹{chunk:,.0f} @ {int(rate*100)}% = ₹{slab_tax:,.0f}")
            remaining -= chunk

        # Section 87A rebate
        rebate = 0
        if taxable <= 700000:
            rebate = min(tax, 25000)
            tax = max(0, tax - rebate)

        # 4% cess
        cess = tax * 0.04
        total_tax = tax + cess

        result = (
            f"Tax Estimate (New Regime FY 2024-25):\n"
            f"  Gross Income       : ₹{annual_income:,.0f}\n"
            f"  Standard Deduction : ₹{standard_deduction:,.0f}\n"
            f"  Taxable Income     : ₹{taxable:,.0f}\n"
            f"  Tax Breakdown:\n" + "\n".join(breakdown) + "\n"
            f"  87A Rebate         : ₹{rebate:,.0f}\n"
            f"  Health & Edu Cess  : ₹{cess:,.0f}\n"
            f"  Total Tax Payable  : ₹{total_tax:,.0f}\n"
            f"  Monthly TDS        : ₹{total_tax/12:,.0f}"
        )
        return result
    except Exception as e:
        return f"Tax calculation error: {str(e)}"


# ─────────────────────────────────────────────
# 5. Current Date/Time
# ─────────────────────────────────────────────
def get_current_datetime() -> str:
    now = datetime.now()
    return (
        f"Current Date & Time:\n"
        f"  Date : {now.strftime('%d %B %Y')}\n"
        f"  Time : {now.strftime('%I:%M %p')}\n"
        f"  Day  : {now.strftime('%A')}"
    )


# ─────────────────────────────────────────────
# Dispatcher — called by tool_node
# ─────────────────────────────────────────────
def dispatch_tool(question: str) -> str:
    """
    Parse question and route to the correct tool.
    Returns a formatted string result in all cases.
    """
    q = question.lower()

    # Extract numbers from question
    numbers = [float(x.replace(",", "")) for x in re.findall(r"[\d,]+\.?\d*", question)]

    # SIP
    if any(w in q for w in ["sip", "systematic investment"]):
        if len(numbers) >= 3:
            return calculate_sip(numbers[0], numbers[1], int(numbers[2]))
        elif len(numbers) == 2:
            return calculate_sip(numbers[0], 12.0, int(numbers[1]))
        return "Please provide: monthly amount, annual return rate (%), and number of years for SIP calculation."

    # EMI / Loan
    if any(w in q for w in ["emi", "loan", "home loan", "personal loan"]):
        if len(numbers) >= 3:
            return calculate_emi(numbers[0], numbers[1], int(numbers[2]))
        return "Please provide: loan amount, annual interest rate (%), and tenure in years for EMI calculation."

    # Compound interest
    if any(w in q for w in ["compound interest", "compound", "fd", "fixed deposit"]):
        if len(numbers) >= 3:
            return calculate_compound_interest(numbers[0], numbers[1], int(numbers[2]))
        return "Please provide: principal, annual rate (%), and number of years."

    # Tax
    if any(w in q for w in ["tax", "income tax", "tds", "itr"]):
        if numbers:
            income = numbers[0]
            if income < 10000:
                income *= 100000  # assume lakhs
            return estimate_tax(income)
        return "Please provide your annual income to estimate tax."

    # Date/time
    if any(w in q for w in ["date", "time", "today", "day", "current"]):
        return get_current_datetime()

    return "I could not determine which calculation to perform. Please specify: SIP, EMI, compound interest, or tax calculation."
