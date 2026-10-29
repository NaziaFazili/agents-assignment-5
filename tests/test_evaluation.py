"""
Test harness for Part 4: LangSmith Tracing + Evaluation.

Verifies evaluator factories return callables, dataset structure,
and LangSmith configuration without requiring API keys.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def check_risk_evaluator_factory():
    """Verify create_risk_accuracy_evaluator returns a callable."""
    try:
        from backend.evaluation.evaluators import create_risk_accuracy_evaluator
        evaluator = create_risk_accuracy_evaluator()
        if callable(evaluator):
            print("[PASS] create_risk_accuracy_evaluator returns a callable")
            return True
        else:
            print("[FAIL] create_risk_accuracy_evaluator did not return a callable")
            return False
    except NotImplementedError:
        print("[EXPECTED] create_risk_accuracy_evaluator raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_consistency_evaluator_factory():
    """Verify create_approval_consistency_evaluator returns a callable."""
    try:
        from backend.evaluation.evaluators import create_approval_consistency_evaluator
        evaluator = create_approval_consistency_evaluator()
        if callable(evaluator):
            print("[PASS] create_approval_consistency_evaluator returns a callable")
            return True
        else:
            print("[FAIL] create_approval_consistency_evaluator did not return a callable")
            return False
    except NotImplementedError:
        print("[EXPECTED] create_approval_consistency_evaluator raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_risk_evaluator_exact_match():
    """Verify risk evaluator returns score 1.0 for exact match."""
    try:
        from backend.evaluation.evaluators import create_risk_accuracy_evaluator
        evaluator = create_risk_accuracy_evaluator()
        result = evaluator(
            inputs={"amount": 500, "department": "engineering", "description": "test"},
            outputs={"risk_level": "low"},
            reference_outputs={"risk_level": "low"},
        )
        if result.get("score") == 1.0:
            print("[PASS] Risk evaluator returns 1.0 for exact match")
            return True
        else:
            print(f"[FAIL] Risk evaluator returned {result.get('score')} instead of 1.0")
            return False
    except NotImplementedError:
        print("[EXPECTED] Risk evaluator not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_risk_evaluator_adjacent():
    """Verify risk evaluator returns score 0.5 for adjacent levels."""
    try:
        from backend.evaluation.evaluators import create_risk_accuracy_evaluator
        evaluator = create_risk_accuracy_evaluator()
        result = evaluator(
            inputs={"amount": 500, "department": "engineering", "description": "test"},
            outputs={"risk_level": "low"},
            reference_outputs={"risk_level": "medium"},
        )
        if result.get("score") == 0.5:
            print("[PASS] Risk evaluator returns 0.5 for adjacent levels")
            return True
        else:
            print(f"[FAIL] Risk evaluator returned {result.get('score')} instead of 0.5")
            return False
    except NotImplementedError:
        print("[EXPECTED] Risk evaluator not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_risk_evaluator_mismatch():
    """Verify risk evaluator returns score 0.0 for non-adjacent levels."""
    try:
        from backend.evaluation.evaluators import create_risk_accuracy_evaluator
        evaluator = create_risk_accuracy_evaluator()
        result = evaluator(
            inputs={"amount": 500, "department": "engineering", "description": "test"},
            outputs={"risk_level": "low"},
            reference_outputs={"risk_level": "critical"},
        )
        if result.get("score") == 0.0:
            print("[PASS] Risk evaluator returns 0.0 for non-adjacent levels")
            return True
        else:
            print(f"[FAIL] Risk evaluator returned {result.get('score')} instead of 0.0")
            return False
    except NotImplementedError:
        print("[EXPECTED] Risk evaluator not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_consistency_evaluator_match():
    """Verify consistency evaluator returns 1.0 for matching status."""
    try:
        from backend.evaluation.evaluators import create_approval_consistency_evaluator
        evaluator = create_approval_consistency_evaluator()
        result = evaluator(
            inputs={"amount": 500, "department": "engineering"},
            outputs={"status": "approved"},
            reference_outputs={"status": "approved"},
        )
        if result.get("score") == 1.0:
            print("[PASS] Consistency evaluator returns 1.0 for match")
            return True
        else:
            print(f"[FAIL] Consistency evaluator returned {result.get('score')} instead of 1.0")
            return False
    except NotImplementedError:
        print("[EXPECTED] Consistency evaluator not implemented (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def check_dataset_structure():
    """Verify evaluation dataset has correct structure."""
    try:
        from backend.evaluation.dataset import EVAL_DATASET

        if len(EVAL_DATASET) < 5:
            print(f"[FAIL] Dataset has only {len(EVAL_DATASET)} cases (need >= 5)")
            return False
        print(f"[PASS] Dataset has {len(EVAL_DATASET)} test cases (>= 5)")

        results = [True]
        for i, case in enumerate(EVAL_DATASET):
            if "input" not in case:
                print(f"[FAIL] Test case {i+1} missing 'input' key")
                results.append(False)
                continue
            if "expected" not in case:
                print(f"[FAIL] Test case {i+1} missing 'expected' key")
                results.append(False)
                continue
            if "risk_level" not in case["expected"]:
                print(f"[FAIL] Test case {i+1} expected missing 'risk_level'")
                results.append(False)
                continue
            results.append(True)

        if all(results):
            print("[PASS] All test cases have correct structure (input, expected.risk_level)")

        return results
    except ImportError as e:
        print(f"[FAIL] Cannot import dataset: {e}")
        return [False]


def check_langsmith_config():
    """Verify LangSmith project config is set."""
    try:
        from backend.config import LANGSMITH_PROJECT
        if LANGSMITH_PROJECT and isinstance(LANGSMITH_PROJECT, str):
            print(f"[PASS] LANGSMITH_PROJECT is set: '{LANGSMITH_PROJECT}'")
            return True
        else:
            print("[FAIL] LANGSMITH_PROJECT is empty or not a string")
            return False
    except ImportError as e:
        print(f"[FAIL] Cannot import config: {e}")
        return False


def run_all_checks():
    """Run all evaluation checks."""
    print("=" * 60)
    print("Part 4: LangSmith Evaluation Tests")
    print("=" * 60)

    all_results = []

    print("\n--- Evaluator Factories ---")
    all_results.append(check_risk_evaluator_factory())
    all_results.append(check_consistency_evaluator_factory())

    print("\n--- Risk Evaluator Logic ---")
    all_results.append(check_risk_evaluator_exact_match())
    all_results.append(check_risk_evaluator_adjacent())
    all_results.append(check_risk_evaluator_mismatch())

    print("\n--- Consistency Evaluator Logic ---")
    all_results.append(check_consistency_evaluator_match())

    print("\n--- Dataset Structure ---")
    dataset_results = check_dataset_structure()
    if isinstance(dataset_results, list):
        all_results.extend(dataset_results)
    else:
        all_results.append(dataset_results)

    print("\n--- LangSmith Config ---")
    all_results.append(check_langsmith_config())

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

def test_risk_evaluator_factory():
    assert check_risk_evaluator_factory()

def test_consistency_evaluator_factory():
    assert check_consistency_evaluator_factory()

def test_risk_evaluator_exact_match():
    assert check_risk_evaluator_exact_match()

def test_risk_evaluator_adjacent():
    assert check_risk_evaluator_adjacent()

def test_risk_evaluator_mismatch():
    assert check_risk_evaluator_mismatch()

def test_consistency_evaluator_match():
    assert check_consistency_evaluator_match()

def test_dataset_structure():
    results = check_dataset_structure()
    if isinstance(results, list):
        assert all(results)
    else:
        assert results

def test_langsmith_config():
    assert check_langsmith_config()
