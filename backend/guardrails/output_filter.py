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
    text = re.sub(PII_PATTERNS["ssn"], "***-**-XXXX", text)
    text = re.sub(PII_PATTERNS["credit_card"], "****-****-****-XXXX", text)
    text = re.sub(PII_PATTERNS["email"], "[EMAIL REDACTED]", text)
    text = re.sub(PII_PATTERNS["phone"], "***-***-XXXX", text)

    return text


def mask_financial_details(text: str) -> str:
    """
    Mask specific financial details in output while preserving context.


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

    # Mask dollar amounts
    def mask_amount(match):
        amount = match.group()
        return "$***" + amount[-5:]

    text = re.sub(r"\$[\d,]+\.\d{2}", mask_amount, text)

    # Mask account numbers
    def mask_account(match):
        account = match.group()
        return "*" * (len(account) - 4) + account[-4:]

    text = re.sub(r"\b\d{8,}\b", mask_account, text)

    return text
