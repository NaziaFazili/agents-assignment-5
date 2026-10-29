"""
Input validation guardrails for the Financial Approval System.

Students implement validation functions that enforce safety rules
on incoming financial requests.

Part 2: Safety Guardrails (10 points from this file)
"""

from backend.config import BUDGET_CEILING, VALID_DEPARTMENTS

# --- GIVEN: Blocked patterns for SQL injection detection ---
BLOCKED_PATTERNS = [
    "drop table", "delete from", "insert into", "update set",
    "union select", "' or '1'='1", "'; --", "<script>",
    "javascript:", "onclick=", "onerror=", "eval(",
    "__import__", "os.system", "subprocess",
]

# --- GIVEN: Maximum field lengths ---
MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 2000
MAX_JUSTIFICATION_LENGTH = 2000


def validate_request(
    amount: float,
    department: str,
    title: str,
    description: str,
    justification: str,
) -> tuple[bool, str]:
    """
    Validate a financial request against safety rules.

    TODO (5 points):
    - Reject if amount <= 0 (message: "Amount must be positive")
    - Reject if amount > BUDGET_CEILING (message: "Amount exceeds budget ceiling of ${BUDGET_CEILING:,.2f}")
    - Reject if department not in VALID_DEPARTMENTS (message: "Invalid department: {department}")
    - Reject if title exceeds MAX_TITLE_LENGTH (message: "Title too long")
    - Call sanitize_text() on title, description, and justification
      - If any returns (False, message), reject with that message
    - If all checks pass, return (True, "Request validated successfully")

    Args:
        amount: Requested dollar amount
        department: Department name
        title: Request title
        description: Request description
        justification: Business justification

    Returns:
        Tuple of (is_valid, message)
    """
    raise NotImplementedError("TODO: Implement validate_request (5 points)")


def validate_amount(amount: float) -> tuple[bool, str]:
    """
    Validate the requested amount.

    TODO (2 points):
    - Return (False, "Amount must be positive") if amount <= 0
    - Return (False, "Amount exceeds budget ceiling of ${BUDGET_CEILING:,.2f}") if amount > BUDGET_CEILING
    - Return (True, "Amount is valid") otherwise

    Args:
        amount: Dollar amount to validate

    Returns:
        Tuple of (is_valid, message)
    """
    raise NotImplementedError("TODO: Implement validate_amount (2 points)")


def sanitize_text(text: str, field_name: str = "text") -> tuple[bool, str]:
    """
    Check text for injection attacks and malicious content.

    TODO (3 points):
    - Convert text to lowercase for comparison
    - Check if any BLOCKED_PATTERNS appear in the lowercased text
    - If found, return (False, "Blocked content detected in {field_name}: suspicious pattern")
    - If clean, return (True, text)  — return the ORIGINAL text, not lowercased

    Args:
        text: The text to sanitize
        field_name: Name of the field (for error messages)

    Returns:
        Tuple of (is_safe, original_text_or_error_message)
    """
    raise NotImplementedError("TODO: Implement sanitize_text (3 points)")
