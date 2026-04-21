# finsage/src/tools/__init__.py

from src.tools.finance_tools import (
    calculate_sip,
    calculate_emi,
    calculate_compound_interest,
    estimate_tax,
    get_current_datetime,
    dispatch_tool,
)

# Alias (optional, for naming consistency)
compound_interest = calculate_compound_interest
estimate_income_tax = estimate_tax

# Unified entry point
run_tool = dispatch_tool

__all__ = [
    "calculate_sip",
    "calculate_emi",
    "calculate_compound_interest",
    "compound_interest",          # alias
    "estimate_tax",
    "estimate_income_tax",        # alias
    "get_current_datetime",
    "dispatch_tool",
    "run_tool",
]