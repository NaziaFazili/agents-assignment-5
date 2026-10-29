"""
Output filtering guardrails for the Financial Approval System.

Students implement output sanitization that masks PII and
sensitive financial details before responses reach users.

Part 2: Safety Guardrails (10 points from this file)
"""

import re

# --- GIVEN: PII detection patterns ---
PII_PATTERNS = {
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
}


def sanitize_output(text: str) -> str:
    """
    Remove PII and sensitive information from output text.

    TODO (5 points):
    - For each pattern in PII_PATTERNS:
      - "ssn": replace matches with "***-**-XXXX" (preserve nothing)
      - "credit_card": replace matches with "****-****-****-XXXX"
      - "email": replace matches with "[EMAIL REDACTED]"
      - "phone": replace matches with "***-***-XXXX"
    - Return the sanitized text

    Args:
        text: Output text that may contain PII

    Returns:
        Sanitized text with PII masked
    """
    raise NotImplementedError("TODO: Implement sanitize_output (5 points)")


def mask_financial_details(text: str) -> str:
    r"""
    Mask specific financial details in output while preserving context.

    TODO (5 points):
    - Find dollar amounts matching pattern $X,XXX.XX or $XXXXX.XX
    - Replace with masked version showing only last 3 digits: $***XX.XX
    - Find account numbers (8+ consecutive digits) and mask all but last 4
    - Return the masked text

    Hints:
    - Use re.sub with a replacement function for dollar amounts
    - Pattern for dollars: r'\$[\d,]+\.?\d*'
    - Pattern for account numbers: r'\b\d{8,}\b'

    Args:
        text: Text containing financial details

    Returns:
        Text with financial details masked
    """
    raise NotImplementedError("TODO: Implement mask_financial_details (5 points)")
