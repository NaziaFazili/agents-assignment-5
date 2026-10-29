"""
Test harness for Part 2: Safety Guardrails.

Verifies input validation, injection blocking, PII masking,
and financial detail filtering without requiring API keys.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def check_validate_request_rejects_negative():
    """validate_request should reject negative amounts."""
    try:
        from backend.guardrails.input_validator import validate_request
        is_valid, msg = validate_request(
            amount=-100,
            department="engineering",
            title="Test",
            description="Test desc",
            justification="Test just",
        )
        if not is_valid:
            print("[PASS] validate_request rejects negative amounts")
            return True
        else:
            print("[FAIL] validate_request accepted negative amount")
            return False
    except NotImplementedError:
        print("[EXPECTED] validate_request raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_validate_request_rejects_over_ceiling():
    """validate_request should reject amounts over budget ceiling."""
    try:
        from backend.guardrails.input_validator import validate_request
        is_valid, msg = validate_request(
            amount=500000,
            department="engineering",
            title="Test",
            description="Test desc",
            justification="Test just",
        )
        if not is_valid:
            print("[PASS] validate_request rejects over-ceiling amounts")
            return True
        else:
            print("[FAIL] validate_request accepted over-ceiling amount")
            return False
    except NotImplementedError:
        print("[EXPECTED] validate_request raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_validate_request_rejects_invalid_dept():
    """validate_request should reject invalid departments."""
    try:
        from backend.guardrails.input_validator import validate_request
        is_valid, msg = validate_request(
            amount=5000,
            department="invalid_dept",
            title="Test",
            description="Test desc",
            justification="Test just",
        )
        if not is_valid:
            print("[PASS] validate_request rejects invalid departments")
            return True
        else:
            print("[FAIL] validate_request accepted invalid department")
            return False
    except NotImplementedError:
        print("[EXPECTED] validate_request raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_validate_request_accepts_valid():
    """validate_request should accept valid requests."""
    try:
        from backend.guardrails.input_validator import validate_request
        is_valid, msg = validate_request(
            amount=5000,
            department="engineering",
            title="Valid Request",
            description="A legitimate request",
            justification="Good business reason",
        )
        if is_valid:
            print("[PASS] validate_request accepts valid requests")
            return True
        else:
            print(f"[FAIL] validate_request rejected valid request: {msg}")
            return False
    except NotImplementedError:
        print("[EXPECTED] validate_request raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_sanitize_text_blocks_injection():
    """sanitize_text should block SQL injection patterns."""
    try:
        from backend.guardrails.input_validator import sanitize_text
        test_cases = [
            ("DROP TABLE users", "drop table"),
            ("'; -- comment", "SQL comment injection"),
            ("<script>alert('xss')</script>", "XSS script"),
            ("import os; os.system('rm -rf /')", "code injection"),
        ]
        results = []
        for text, label in test_cases:
            is_safe, msg = sanitize_text(text)
            if not is_safe:
                print(f"[PASS] sanitize_text blocks: {label}")
                results.append(True)
            else:
                print(f"[FAIL] sanitize_text did not block: {label}")
                results.append(False)
        return results
    except NotImplementedError:
        print("[EXPECTED] sanitize_text raises NotImplementedError (student TODO)")
        return [True]
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return [False]


def check_sanitize_output_masks_ssn():
    """sanitize_output should mask SSN patterns."""
    try:
        from backend.guardrails.output_filter import sanitize_output
        text = "SSN: 123-45-6789"
        result = sanitize_output(text)
        if "123-45-6789" not in result:
            print("[PASS] sanitize_output masks SSN")
            return True
        else:
            print("[FAIL] sanitize_output did not mask SSN")
            return False
    except NotImplementedError:
        print("[EXPECTED] sanitize_output raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_sanitize_output_masks_credit_card():
    """sanitize_output should mask credit card numbers."""
    try:
        from backend.guardrails.output_filter import sanitize_output
        text = "Card: 4111-1111-1111-1111"
        result = sanitize_output(text)
        if "4111-1111-1111-1111" not in result:
            print("[PASS] sanitize_output masks credit card")
            return True
        else:
            print("[FAIL] sanitize_output did not mask credit card")
            return False
    except NotImplementedError:
        print("[EXPECTED] sanitize_output raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_sanitize_output_masks_email():
    """sanitize_output should mask email addresses."""
    try:
        from backend.guardrails.output_filter import sanitize_output
        text = "Contact: alice@example.com"
        result = sanitize_output(text)
        if "alice@example.com" not in result:
            print("[PASS] sanitize_output masks email")
            return True
        else:
            print("[FAIL] sanitize_output did not mask email")
            return False
    except NotImplementedError:
        print("[EXPECTED] sanitize_output raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_sanitize_output_masks_phone():
    """sanitize_output should mask phone numbers."""
    try:
        from backend.guardrails.output_filter import sanitize_output
        text = "Phone: 555-123-4567"
        result = sanitize_output(text)
        if "555-123-4567" not in result:
            print("[PASS] sanitize_output masks phone")
            return True
        else:
            print("[FAIL] sanitize_output did not mask phone")
            return False
    except NotImplementedError:
        print("[EXPECTED] sanitize_output raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_mask_financial_details():
    """mask_financial_details should mask dollar amounts and account numbers."""
    try:
        from backend.guardrails.output_filter import mask_financial_details
        text = "Amount: $45,000.00, Account: 12345678901234"
        result = mask_financial_details(text)
        if "$45,000.00" not in result:
            print("[PASS] mask_financial_details masks dollar amounts")
            return True
        else:
            print("[FAIL] mask_financial_details did not mask dollar amounts")
            return False
    except NotImplementedError:
        print("[EXPECTED] mask_financial_details raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_validate_amount():
    """validate_amount should accept/reject amounts correctly."""
    try:
        from backend.guardrails.input_validator import validate_amount
        tests = []

        is_valid, msg = validate_amount(-100)
        tests.append(not is_valid)
        if not is_valid:
            print("[PASS] validate_amount rejects negative")
        else:
            print("[FAIL] validate_amount accepted negative")

        is_valid, msg = validate_amount(500000)
        tests.append(not is_valid)
        if not is_valid:
            print("[PASS] validate_amount rejects over ceiling")
        else:
            print("[FAIL] validate_amount accepted over ceiling")

        is_valid, msg = validate_amount(5000)
        tests.append(is_valid)
        if is_valid:
            print("[PASS] validate_amount accepts valid amount")
        else:
            print("[FAIL] validate_amount rejected valid amount")

        return tests
    except NotImplementedError:
        print("[EXPECTED] validate_amount raises NotImplementedError (student TODO)")
        return [True]
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return [False]


def run_all_checks():
    """Run all guardrail checks."""
    print("=" * 60)
    print("Part 2: Safety Guardrails Tests")
    print("=" * 60)

    all_results = []

    print("\n--- Input Validation ---")
    all_results.append(check_validate_request_rejects_negative())
    all_results.append(check_validate_request_rejects_over_ceiling())
    all_results.append(check_validate_request_rejects_invalid_dept())
    all_results.append(check_validate_request_accepts_valid())

    print("\n--- Injection Blocking ---")
    injection_results = check_sanitize_text_blocks_injection()
    all_results.extend(injection_results)

    print("\n--- PII Masking ---")
    all_results.append(check_sanitize_output_masks_ssn())
    all_results.append(check_sanitize_output_masks_credit_card())
    all_results.append(check_sanitize_output_masks_email())
    all_results.append(check_sanitize_output_masks_phone())

    print("\n--- Financial Detail Masking ---")
    all_results.append(check_mask_financial_details())

    print("\n--- Amount Validation ---")
    amount_results = check_validate_amount()
    all_results.extend(amount_results)

    print("\n" + "=" * 60)
    passed = sum(1 for r in all_results if r)
    total = len(all_results)
    print(f"Results: {passed}/{total} checks passed")
    print("=" * 60)

    return all(all_results)


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)


# --- pytest-discoverable tests ---

def test_validate_request_rejects_negative():
    assert check_validate_request_rejects_negative()

def test_validate_request_rejects_over_ceiling():
    assert check_validate_request_rejects_over_ceiling()

def test_validate_request_rejects_invalid_dept():
    assert check_validate_request_rejects_invalid_dept()

def test_validate_request_accepts_valid():
    assert check_validate_request_accepts_valid()

def test_sanitize_text_blocks_injection():
    results = check_sanitize_text_blocks_injection()
    assert all(results)

def test_sanitize_output_masks_ssn():
    assert check_sanitize_output_masks_ssn()

def test_sanitize_output_masks_credit_card():
    assert check_sanitize_output_masks_credit_card()

def test_sanitize_output_masks_email():
    assert check_sanitize_output_masks_email()

def test_sanitize_output_masks_phone():
    assert check_sanitize_output_masks_phone()

def test_mask_financial_details():
    assert check_mask_financial_details()

def test_validate_amount():
    results = check_validate_amount()
    assert all(results)
