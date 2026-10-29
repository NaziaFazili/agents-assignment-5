"""
Runner for the Three-Layer Evaluation Framework.

Imports all evaluator factories, runs them against a dataset,
and prints a report card grouped by layer. Runs locally: it sends
nothing to LangSmith.

This file is GIVEN — students do not modify it.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv

# Load .env before any RAGAS metric runs: RAGAS reads RAGAS_DO_NOT_TRACK once,
# on its first analytics event, and some metrics run before get_llm() loads .env.
load_dotenv()

from backend.evaluation.dataset import EVAL_DATASET
from backend.evaluation.three_layer_evaluators import (
    create_approval_path_evaluator,
    create_false_positive_evaluator,
    create_false_negative_evaluator,
    create_human_review_efficiency_evaluator,
    create_tool_call_accuracy_evaluator,
    create_agent_goal_accuracy_evaluator,
    create_topic_adherence_evaluator,
    create_policy_adherence_evaluator,
    create_hallucination_evaluator,
    create_audit_trail_evaluator,
    HUMAN_REVIEW_STAGES,
)


# ---------------------------------------------------------------------------
# Evaluator registry — maps name → (factory, layer, points)
# ---------------------------------------------------------------------------
EVALUATOR_REGISTRY = {
    # Layer 1 — Business Metrics
    "approval_path": (create_approval_path_evaluator, 1, 3),
    "false_positive": (create_false_positive_evaluator, 1, 2),
    "false_negative": (create_false_negative_evaluator, 1, 2),
    "human_review_efficiency": (create_human_review_efficiency_evaluator, 1, 3),
    # Layer 2 — Agent Performance
    "tool_call_accuracy": (create_tool_call_accuracy_evaluator, 2, 5),
    "agent_goal_accuracy": (create_agent_goal_accuracy_evaluator, 2, 4),
    "topic_adherence": (create_topic_adherence_evaluator, 2, 3),
    # Layer 3 — Safety & Compliance
    "policy_adherence": (create_policy_adherence_evaluator, 3, 4),
    "hallucination": (create_hallucination_evaluator, 3, 4),
    "audit_trail": (create_audit_trail_evaluator, 3, 4),
}

LAYER_NAMES = {
    1: "Business Metrics",
    2: "Agent Performance",
    3: "Safety & Compliance",
}


def _review_decisions(expected):
    """One decision per human review stage in the expected path, like the review
    nodes record them. If the request is rejected after a review, the last review
    is the rejecting one."""
    reviews = [s for s in expected.get("approval_path", []) if s in HUMAN_REVIEW_STAGES]
    decisions = []
    for i, stage in enumerate(reviews):
        rejected = expected.get("status") == "rejected" and i == len(reviews) - 1
        decision = "rejected" if rejected else "approved"
        decisions.append({"stage": stage, "decision": decision,
                          "reasoning": f"{decision.capitalize()} at {stage}"})
    return decisions


def _instantiate_evaluators():
    """Try to create each evaluator; return {name: callable_or_None}."""
    evaluators = {}
    for name, (factory, _layer, _pts) in EVALUATOR_REGISTRY.items():
        try:
            evaluators[name] = factory()
        except NotImplementedError:
            evaluators[name] = None
        except Exception as e:
            print(f"  Warning: {name} factory raised {type(e).__name__}: {e}")
            evaluators[name] = None
    return evaluators


def _run_evaluator(evaluator, inputs, outputs, reference_outputs):
    """Run a single evaluator and return the score (or None on error)."""
    try:
        result = evaluator(
            inputs=inputs,
            outputs=outputs,
            reference_outputs=reference_outputs,
        )
        return result.get("score")
    except NotImplementedError:
        return None
    except Exception as e:
        print(f"    Error: {e}")
        return None


def run_three_layer_evaluation(dataset=None):
    """
    Run all three-layer evaluators against the dataset.

    Args:
        dataset: list[dict] with "input" and "expected" keys.
                 Defaults to EVAL_DATASET from dataset.py.
    """
    if dataset is None:
        dataset = EVAL_DATASET

    print()
    print("=" * 50)
    print("  Three-Layer Evaluation Framework")
    print("=" * 50)
    print(f"  Dataset: {len(dataset)} test cases")
    print()

    evaluators = _instantiate_evaluators()

    implemented = sum(1 for v in evaluators.values() if v is not None)
    total = len(evaluators)
    print(f"  Evaluators: {implemented}/{total} implemented")
    print()

    # Collect scores per evaluator across all test cases
    all_scores = {name: [] for name in EVALUATOR_REGISTRY}

    for i, test_case in enumerate(dataset):
        inputs = test_case["input"]
        expected = test_case["expected"]

        # Build outputs dict — in a real setup this comes from running the agent.
        # For scaffolding evaluation, we use expected as a stand-in for outputs.
        outputs = {
            "status": expected.get("status", ""),
            "risk_level": expected.get("risk_level", ""),
            "approval_path": expected.get("approval_path", []),
            "human_reviews": expected.get("human_reviews", 0),
            "decisions": expected.get("decisions", _review_decisions(expected)),
        }

        for name, evaluator in evaluators.items():
            if evaluator is None:
                continue
            score = _run_evaluator(evaluator, inputs, outputs, expected)
            if score is not None:
                all_scores[name].append(score)

    # --- Report card ---
    print()
    print("\u2550" * 50)
    print("  Three-Layer Evaluation Report")
    print("\u2550" * 50)

    layer_scores = {1: [], 2: [], 3: []}

    for name, (_, layer, pts) in EVALUATOR_REGISTRY.items():
        scores = all_scores[name]
        if scores:
            avg = sum(scores) / len(scores)
            layer_scores[layer].append(avg)
            status = f"{avg:.2f}"
        else:
            status = "NOT IMPLEMENTED"
        print(f"  {name:30s}  {status}")

    print()
    print("\u2500" * 50)

    overall_scores = []
    for layer_num in sorted(LAYER_NAMES):
        scores = layer_scores[layer_num]
        if scores:
            avg = sum(scores) / len(scores)
            overall_scores.append(avg)
            print(f"  Layer {layer_num} - {LAYER_NAMES[layer_num]:25s} {avg:.2f}")
        else:
            print(f"  Layer {layer_num} - {LAYER_NAMES[layer_num]:25s} N/A")

    print("\u2500" * 50)
    if overall_scores:
        overall = sum(overall_scores) / len(overall_scores)
        print(f"  {'Overall Score':36s} {overall:.2f}")
    else:
        print(f"  {'Overall Score':36s} N/A (no evaluators implemented)")
    print("\u2550" * 50)
    print()


if __name__ == "__main__":
    run_three_layer_evaluation()
