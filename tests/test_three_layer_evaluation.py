"""
Test harness for Part 5: Three-Layer Evaluation Framework.

Verifies evaluator factories, dataset generator, and validation logic
without requiring RAGAS or LangSmith API keys.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ═══════════════════════════════════════════════════════════════════════════
# Layer 1 — Business Metrics Factory Tests
# ═══════════════════════════════════════════════════════════════════════════

def check_approval_path_evaluator_factory():
    """Verify create_approval_path_evaluator returns a callable."""
    try:
        from backend.evaluation.three_layer_evaluators import create_approval_path_evaluator
        evaluator = create_approval_path_evaluator()
        if callable(evaluator):
            print("[PASS] create_approval_path_evaluator returns a callable")
            return True
        else:
            print("[FAIL] create_approval_path_evaluator did not return a callable")
            return False
    except NotImplementedError:
        print("[EXPECTED] create_approval_path_evaluator raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_false_positive_evaluator_factory():
    """Verify create_false_positive_evaluator returns a callable."""
    try:
        from backend.evaluation.three_layer_evaluators import create_false_positive_evaluator
        evaluator = create_false_positive_evaluator()
        if callable(evaluator):
            print("[PASS] create_false_positive_evaluator returns a callable")
            return True
        else:
            print("[FAIL] create_false_positive_evaluator did not return a callable")
            return False
    except NotImplementedError:
        print("[EXPECTED] create_false_positive_evaluator raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_false_negative_evaluator_factory():
    """Verify create_false_negative_evaluator returns a callable."""
    try:
        from backend.evaluation.three_layer_evaluators import create_false_negative_evaluator
        evaluator = create_false_negative_evaluator()
        if callable(evaluator):
            print("[PASS] create_false_negative_evaluator returns a callable")
            return True
        else:
            print("[FAIL] create_false_negative_evaluator did not return a callable")
            return False
    except NotImplementedError:
        print("[EXPECTED] create_false_negative_evaluator raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_human_review_efficiency_factory():
    """Verify create_human_review_efficiency_evaluator returns a callable."""
    try:
        from backend.evaluation.three_layer_evaluators import create_human_review_efficiency_evaluator
        evaluator = create_human_review_efficiency_evaluator()
        if callable(evaluator):
            print("[PASS] create_human_review_efficiency_evaluator returns a callable")
            return True
        else:
            print("[FAIL] create_human_review_efficiency_evaluator did not return a callable")
            return False
    except NotImplementedError:
        print("[EXPECTED] create_human_review_efficiency_evaluator raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# Layer 1 — Behavior Tests
# ═══════════════════════════════════════════════════════════════════════════

def check_approval_path_exact_match():
    """Verify approval path evaluator returns 1.0 for exact match."""
    try:
        from backend.evaluation.three_layer_evaluators import create_approval_path_evaluator
        evaluator = create_approval_path_evaluator()
        path = ["submit_request", "assess_risk", "validate_budget", "process_request"]
        result = evaluator(
            inputs={"amount": 500, "department": "engineering"},
            outputs={"approval_path": path},
            reference_outputs={"approval_path": path},
        )
        if result.get("score") == 1.0:
            print("[PASS] Approval path evaluator returns 1.0 for exact match")
            return True
        else:
            print(f"[FAIL] Approval path evaluator returned {result.get('score')} instead of 1.0")
            return False
    except NotImplementedError:
        print("[EXPECTED] Approval path evaluator not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_approval_path_length_match():
    """Verify approval path evaluator returns 0.5 for same-length different path."""
    try:
        from backend.evaluation.three_layer_evaluators import create_approval_path_evaluator
        evaluator = create_approval_path_evaluator()
        result = evaluator(
            inputs={"amount": 500, "department": "engineering"},
            outputs={"approval_path": ["submit_request", "assess_risk", "process_request"]},
            reference_outputs={"approval_path": ["submit_request", "manager_review", "process_request"]},
        )
        if result.get("score") == 0.5:
            print("[PASS] Approval path evaluator returns 0.5 for same-length different path")
            return True
        else:
            print(f"[FAIL] Approval path evaluator returned {result.get('score')} instead of 0.5")
            return False
    except NotImplementedError:
        print("[EXPECTED] Approval path evaluator not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_false_positive_detection():
    """Verify false positive evaluator returns 0.0 when legit request is rejected."""
    try:
        from backend.evaluation.three_layer_evaluators import create_false_positive_evaluator
        evaluator = create_false_positive_evaluator()
        result = evaluator(
            inputs={"amount": 500, "department": "engineering"},
            outputs={"status": "approved"},
            reference_outputs={"status": "rejected"},
        )
        if result.get("score") == 0.0:
            print("[PASS] False positive evaluator returns 0.0 for approved-when-should-reject")
            return True
        else:
            print(f"[FAIL] False positive evaluator returned {result.get('score')} instead of 0.0")
            return False
    except NotImplementedError:
        print("[EXPECTED] False positive evaluator not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_false_negative_detection():
    """Verify false negative evaluator returns 0.0 when valid request is rejected."""
    try:
        from backend.evaluation.three_layer_evaluators import create_false_negative_evaluator
        evaluator = create_false_negative_evaluator()
        result = evaluator(
            inputs={"amount": 500, "department": "engineering"},
            outputs={"status": "rejected"},
            reference_outputs={"status": "approved"},
        )
        if result.get("score") == 0.0:
            print("[PASS] False negative evaluator returns 0.0 for rejected-when-should-approve")
            return True
        else:
            print(f"[FAIL] False negative evaluator returned {result.get('score')} instead of 0.0")
            return False
    except NotImplementedError:
        print("[EXPECTED] False negative evaluator not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_human_review_exact():
    """Verify human review evaluator returns 1.0 for exact match."""
    try:
        from backend.evaluation.three_layer_evaluators import create_human_review_efficiency_evaluator
        evaluator = create_human_review_efficiency_evaluator()
        result = evaluator(
            inputs={"amount": 500, "department": "engineering"},
            outputs={"human_reviews": 2},
            reference_outputs={"human_reviews": 2},
        )
        if result.get("score") == 1.0:
            print("[PASS] Human review evaluator returns 1.0 for exact match")
            return True
        else:
            print(f"[FAIL] Human review evaluator returned {result.get('score')} instead of 1.0")
            return False
    except NotImplementedError:
        print("[EXPECTED] Human review evaluator not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_human_review_off_by_one():
    """Verify human review evaluator returns 0.5 for off-by-one."""
    try:
        from backend.evaluation.three_layer_evaluators import create_human_review_efficiency_evaluator
        evaluator = create_human_review_efficiency_evaluator()
        result = evaluator(
            inputs={"amount": 500, "department": "engineering"},
            outputs={"human_reviews": 1},
            reference_outputs={"human_reviews": 2},
        )
        if result.get("score") == 0.5:
            print("[PASS] Human review evaluator returns 0.5 for off-by-one")
            return True
        else:
            print(f"[FAIL] Human review evaluator returned {result.get('score')} instead of 0.5")
            return False
    except NotImplementedError:
        print("[EXPECTED] Human review evaluator not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# Layer 2 — Agent Performance Factory Tests
# ═══════════════════════════════════════════════════════════════════════════

def check_tool_call_accuracy_factory():
    """Verify create_tool_call_accuracy_evaluator returns a callable."""
    try:
        from backend.evaluation.three_layer_evaluators import create_tool_call_accuracy_evaluator
        evaluator = create_tool_call_accuracy_evaluator()
        if callable(evaluator):
            print("[PASS] create_tool_call_accuracy_evaluator returns a callable")
            return True
        else:
            print("[FAIL] create_tool_call_accuracy_evaluator did not return a callable")
            return False
    except NotImplementedError:
        print("[EXPECTED] create_tool_call_accuracy_evaluator raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_agent_goal_accuracy_factory():
    """Verify create_agent_goal_accuracy_evaluator returns a callable."""
    try:
        from backend.evaluation.three_layer_evaluators import create_agent_goal_accuracy_evaluator
        evaluator = create_agent_goal_accuracy_evaluator()
        if callable(evaluator):
            print("[PASS] create_agent_goal_accuracy_evaluator returns a callable")
            return True
        else:
            print("[FAIL] create_agent_goal_accuracy_evaluator did not return a callable")
            return False
    except NotImplementedError:
        print("[EXPECTED] create_agent_goal_accuracy_evaluator raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_topic_adherence_factory():
    """Verify create_topic_adherence_evaluator returns a callable."""
    try:
        from backend.evaluation.three_layer_evaluators import create_topic_adherence_evaluator
        evaluator = create_topic_adherence_evaluator()
        if callable(evaluator):
            print("[PASS] create_topic_adherence_evaluator returns a callable")
            return True
        else:
            print("[FAIL] create_topic_adherence_evaluator did not return a callable")
            return False
    except NotImplementedError:
        print("[EXPECTED] create_topic_adherence_evaluator raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# Layer 3 — Safety & Compliance Factory Tests
# ═══════════════════════════════════════════════════════════════════════════

def check_policy_adherence_factory():
    """Verify create_policy_adherence_evaluator returns a callable."""
    try:
        from backend.evaluation.three_layer_evaluators import create_policy_adherence_evaluator
        evaluator = create_policy_adherence_evaluator()
        if callable(evaluator):
            print("[PASS] create_policy_adherence_evaluator returns a callable")
            return True
        else:
            print("[FAIL] create_policy_adherence_evaluator did not return a callable")
            return False
    except NotImplementedError:
        print("[EXPECTED] create_policy_adherence_evaluator raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_hallucination_factory():
    """Verify create_hallucination_evaluator returns a callable."""
    try:
        from backend.evaluation.three_layer_evaluators import create_hallucination_evaluator
        evaluator = create_hallucination_evaluator()
        if callable(evaluator):
            print("[PASS] create_hallucination_evaluator returns a callable")
            return True
        else:
            print("[FAIL] create_hallucination_evaluator did not return a callable")
            return False
    except NotImplementedError:
        print("[EXPECTED] create_hallucination_evaluator raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_audit_trail_factory():
    """Verify create_audit_trail_evaluator returns a callable."""
    try:
        from backend.evaluation.three_layer_evaluators import create_audit_trail_evaluator
        evaluator = create_audit_trail_evaluator()
        if callable(evaluator):
            print("[PASS] create_audit_trail_evaluator returns a callable")
            return True
        else:
            print("[FAIL] create_audit_trail_evaluator did not return a callable")
            return False
    except NotImplementedError:
        print("[EXPECTED] create_audit_trail_evaluator raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# Layer 3 — Behavior Tests
# ═══════════════════════════════════════════════════════════════════════════

def check_audit_trail_complete():
    """Verify audit trail evaluator returns 1.0 for complete trail."""
    try:
        from backend.evaluation.three_layer_evaluators import create_audit_trail_evaluator
        evaluator = create_audit_trail_evaluator()
        decisions = [
            {"stage": "manager_review", "decision": "approved", "reasoning": "Justified expense"},
            {"stage": "finance_review", "decision": "approved", "reasoning": "Within annual plan"},
        ]
        result = evaluator(
            inputs={"amount": 75000, "department": "research"},
            outputs={"decisions": decisions},
            reference_outputs={"approval_path": ["submit_request", "assess_risk", "manager_review",
                                                 "finance_review", "process_request"]},
        )
        if result.get("score") == 1.0:
            print("[PASS] Audit trail evaluator returns 1.0 for complete trail")
            return True
        else:
            print(f"[FAIL] Audit trail evaluator returned {result.get('score')} instead of 1.0")
            return False
    except NotImplementedError:
        print("[EXPECTED] Audit trail evaluator not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_audit_trail_no_reviews():
    """Verify audit trail evaluator returns 1.0 for an auto-approved request with no decisions."""
    try:
        from backend.evaluation.three_layer_evaluators import create_audit_trail_evaluator
        evaluator = create_audit_trail_evaluator()
        result = evaluator(
            inputs={"amount": 500, "department": "operations"},
            outputs={"decisions": []},
            reference_outputs={"approval_path": ["submit_request", "assess_risk",
                                                 "validate_budget", "process_request"]},
        )
        if result.get("score") == 1.0:
            print("[PASS] Audit trail evaluator returns 1.0 when no human review was expected")
            return True
        else:
            print(f"[FAIL] Audit trail evaluator returned {result.get('score')} for an auto-approved "
                  "request with no decisions (expected 1.0: only human reviews record decisions)")
            return False
    except NotImplementedError:
        print("[EXPECTED] Audit trail evaluator not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_audit_trail_empty():
    """Verify audit trail evaluator penalizes empty decisions."""
    try:
        from backend.evaluation.three_layer_evaluators import create_audit_trail_evaluator
        evaluator = create_audit_trail_evaluator()
        result = evaluator(
            inputs={"amount": 15000, "department": "engineering"},
            outputs={"decisions": []},
            reference_outputs={"approval_path": ["submit_request", "assess_risk", "manager_review",
                                                 "validate_budget", "process_request"]},
        )
        score = result.get("score", 1.0)
        if score < 1.0:
            print(f"[PASS] Audit trail evaluator penalizes empty decisions (score={score})")
            return True
        else:
            print(f"[FAIL] Audit trail evaluator returned {score} for empty decisions (expected < 1.0)")
            return False
    except NotImplementedError:
        print("[EXPECTED] Audit trail evaluator not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_policy_adherence_over_ceiling():
    """Verify policy evaluator catches over-ceiling approvals."""
    try:
        from backend.evaluation.three_layer_evaluators import create_policy_adherence_evaluator
        evaluator = create_policy_adherence_evaluator()
        result = evaluator(
            inputs={"amount": 150000, "department": "engineering"},
            outputs={"status": "approved", "risk_level": "critical", "human_reviews": 3},
            reference_outputs={"status": "rejected"},
        )
        score = result.get("score", 1.0)
        if score < 1.0:
            print(f"[PASS] Policy evaluator catches over-ceiling approval (score={score})")
            return True
        else:
            print(f"[FAIL] Policy evaluator returned {score} for over-ceiling approval (expected < 1.0)")
            return False
    except NotImplementedError:
        print("[EXPECTED] Policy evaluator not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# Dataset Generator Tests
# ═══════════════════════════════════════════════════════════════════════════

def check_dataset_generator_import():
    """Verify dataset generator module is importable."""
    try:
        from backend.evaluation.dataset_generator import (
            generate_eval_dataset,
            generate_edge_cases,
            upload_to_langsmith,
            validate_generated_dataset,
        )
        print("[PASS] dataset_generator module imports successfully")
        return True
    except ImportError as e:
        print(f"[FAIL] Cannot import dataset_generator: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error importing dataset_generator: {e}")
        return False


def check_validate_good_dataset():
    """Verify validate_generated_dataset accepts valid data."""
    try:
        from backend.evaluation.dataset_generator import validate_generated_dataset
        good_dataset = [
            {
                "input": {
                    "request_id": "TEST-001",
                    "title": "Test Purchase",
                    "description": "A test purchase",
                    "amount": 500.0,
                    "department": "engineering",
                    "requester": "Test User",
                    "justification": "Testing",
                    "priority": "normal",
                },
                "expected": {
                    "risk_level": "low",
                    "status": "approved",
                    "approval_path": ["submit_request", "assess_risk", "process_request"],
                    "human_reviews": 0,
                },
            }
        ]
        is_valid, errors = validate_generated_dataset(good_dataset)
        if is_valid and len(errors) == 0:
            print("[PASS] validate_generated_dataset accepts valid dataset")
            return True
        else:
            print(f"[FAIL] validate_generated_dataset rejected valid dataset: {errors}")
            return False
    except NotImplementedError:
        print("[EXPECTED] validate_generated_dataset not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_validate_bad_dataset():
    """Verify validate_generated_dataset rejects invalid data."""
    try:
        from backend.evaluation.dataset_generator import validate_generated_dataset
        bad_dataset = [
            {
                "input": {"title": "Missing fields"},
                "expected": {"status": "approved"},
            }
        ]
        is_valid, errors = validate_generated_dataset(bad_dataset)
        if not is_valid and len(errors) > 0:
            print(f"[PASS] validate_generated_dataset catches errors ({len(errors)} found)")
            return True
        else:
            print("[FAIL] validate_generated_dataset did not catch invalid data")
            return False
    except NotImplementedError:
        print("[EXPECTED] validate_generated_dataset not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_validate_empty_dataset():
    """Verify validate_generated_dataset rejects empty dataset."""
    try:
        from backend.evaluation.dataset_generator import validate_generated_dataset
        is_valid, errors = validate_generated_dataset([])
        if not is_valid:
            print("[PASS] validate_generated_dataset rejects empty dataset")
            return True
        else:
            print("[FAIL] validate_generated_dataset accepted empty dataset")
            return False
    except NotImplementedError:
        print("[EXPECTED] validate_generated_dataset not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_validate_bad_department():
    """Verify validate_generated_dataset catches invalid department."""
    try:
        from backend.evaluation.dataset_generator import validate_generated_dataset
        bad_dept_dataset = [
            {
                "input": {
                    "request_id": "TEST-001",
                    "title": "Test",
                    "description": "Test",
                    "amount": 500.0,
                    "department": "nonexistent_dept",
                    "requester": "Test User",
                    "justification": "Testing",
                    "priority": "normal",
                },
                "expected": {
                    "risk_level": "low",
                    "status": "approved",
                    "approval_path": ["submit_request"],
                    "human_reviews": 0,
                },
            }
        ]
        is_valid, errors = validate_generated_dataset(bad_dept_dataset)
        if not is_valid:
            print("[PASS] validate_generated_dataset catches invalid department")
            return True
        else:
            print("[FAIL] validate_generated_dataset accepted invalid department")
            return False
    except NotImplementedError:
        print("[EXPECTED] validate_generated_dataset not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# Runner Test
# ═══════════════════════════════════════════════════════════════════════════

def check_runner_import():
    """Verify the three-layer runner is importable."""
    try:
        from backend.evaluation.run_three_layer_eval import run_three_layer_evaluation
        if callable(run_three_layer_evaluation):
            print("[PASS] run_three_layer_eval module imports successfully")
            return True
        else:
            print("[FAIL] run_three_layer_evaluation is not callable")
            return False
    except ImportError as e:
        print(f"[FAIL] Cannot import run_three_layer_eval: {e}")
        return False


def check_constants():
    """Verify helper constants are defined correctly."""
    try:
        from backend.evaluation.three_layer_evaluators import (
            RISK_LEVELS,
            EXPECTED_REVIEWS_BY_RISK,
            BUDGET_CEILING,
        )
        checks = []
        if RISK_LEVELS == ["low", "medium", "high", "critical"]:
            checks.append(True)
        else:
            print(f"[FAIL] RISK_LEVELS incorrect: {RISK_LEVELS}")
            checks.append(False)

        if BUDGET_CEILING == 100_000:
            checks.append(True)
        else:
            print(f"[FAIL] BUDGET_CEILING incorrect: {BUDGET_CEILING}")
            checks.append(False)

        expected_reviews = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        if EXPECTED_REVIEWS_BY_RISK == expected_reviews:
            checks.append(True)
        else:
            print(f"[FAIL] EXPECTED_REVIEWS_BY_RISK incorrect: {EXPECTED_REVIEWS_BY_RISK}")
            checks.append(False)

        if all(checks):
            print("[PASS] All helper constants are defined correctly")
        return all(checks)
    except ImportError as e:
        print(f"[FAIL] Cannot import constants: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# Main runner
# ═══════════════════════════════════════════════════════════════════════════

def run_all_checks():
    """Run all three-layer evaluation checks."""
    print("=" * 60)
    print("Part 5: Three-Layer Evaluation Framework Tests")
    print("=" * 60)

    all_results = []

    print("\n--- Constants ---")
    all_results.append(check_constants())

    print("\n--- Layer 1: Business Metrics Factories ---")
    all_results.append(check_approval_path_evaluator_factory())
    all_results.append(check_false_positive_evaluator_factory())
    all_results.append(check_false_negative_evaluator_factory())
    all_results.append(check_human_review_efficiency_factory())

    print("\n--- Layer 1: Business Metrics Behavior ---")
    all_results.append(check_approval_path_exact_match())
    all_results.append(check_approval_path_length_match())
    all_results.append(check_false_positive_detection())
    all_results.append(check_false_negative_detection())
    all_results.append(check_human_review_exact())
    all_results.append(check_human_review_off_by_one())

    print("\n--- Layer 2: Agent Performance Factories ---")
    all_results.append(check_tool_call_accuracy_factory())
    all_results.append(check_agent_goal_accuracy_factory())
    all_results.append(check_topic_adherence_factory())

    print("\n--- Layer 3: Safety & Compliance Factories ---")
    all_results.append(check_policy_adherence_factory())
    all_results.append(check_hallucination_factory())
    all_results.append(check_audit_trail_factory())

    print("\n--- Layer 3: Safety & Compliance Behavior ---")
    all_results.append(check_audit_trail_complete())
    all_results.append(check_audit_trail_empty())
    all_results.append(check_audit_trail_no_reviews())
    all_results.append(check_policy_adherence_over_ceiling())

    print("\n--- Dataset Generator ---")
    all_results.append(check_dataset_generator_import())
    all_results.append(check_validate_good_dataset())
    all_results.append(check_validate_bad_dataset())
    all_results.append(check_validate_empty_dataset())
    all_results.append(check_validate_bad_department())

    print("\n--- Runner ---")
    all_results.append(check_runner_import())

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

def test_constants():
    assert check_constants()

def test_approval_path_evaluator_factory():
    assert check_approval_path_evaluator_factory()

def test_false_positive_evaluator_factory():
    assert check_false_positive_evaluator_factory()

def test_false_negative_evaluator_factory():
    assert check_false_negative_evaluator_factory()

def test_human_review_efficiency_factory():
    assert check_human_review_efficiency_factory()

def test_approval_path_exact_match():
    assert check_approval_path_exact_match()

def test_approval_path_length_match():
    assert check_approval_path_length_match()

def test_false_positive_detection():
    assert check_false_positive_detection()

def test_false_negative_detection():
    assert check_false_negative_detection()

def test_human_review_exact():
    assert check_human_review_exact()

def test_human_review_off_by_one():
    assert check_human_review_off_by_one()

def test_tool_call_accuracy_factory():
    assert check_tool_call_accuracy_factory()

def test_agent_goal_accuracy_factory():
    assert check_agent_goal_accuracy_factory()

def test_topic_adherence_factory():
    assert check_topic_adherence_factory()

def test_policy_adherence_factory():
    assert check_policy_adherence_factory()

def test_hallucination_factory():
    assert check_hallucination_factory()

def test_audit_trail_factory():
    assert check_audit_trail_factory()

def test_audit_trail_complete():
    assert check_audit_trail_complete()

def test_audit_trail_empty():
    assert check_audit_trail_empty()

def test_audit_trail_no_reviews():
    assert check_audit_trail_no_reviews()

def test_policy_adherence_over_ceiling():
    assert check_policy_adherence_over_ceiling()

def test_dataset_generator_import():
    assert check_dataset_generator_import()

def test_validate_good_dataset():
    assert check_validate_good_dataset()

def test_validate_bad_dataset():
    assert check_validate_bad_dataset()

def test_validate_empty_dataset():
    assert check_validate_empty_dataset()

def test_validate_bad_department():
    assert check_validate_bad_department()

def test_runner_import():
    assert check_runner_import()
