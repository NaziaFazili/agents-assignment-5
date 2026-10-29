"""
Evaluation runner for the Financial Approval System.

Runs the Part 4 evaluators (risk assessment accuracy and approval
consistency) locally over the 12-case dataset. It makes no LLM calls and
sends nothing to LangSmith. LangSmith traces come from the running server
(python -m backend.server) when LANGSMITH_API_KEY holds a real key.
"""

import os
from backend.config import LANGSMITH_API_KEY, LANGSMITH_PROJECT
from backend.evaluation.dataset import EVAL_DATASET
from backend.evaluation.evaluators import (
    create_risk_accuracy_evaluator,
    create_approval_consistency_evaluator,
)


def run_evaluation():
    """
    Run the evaluation pipeline.

    This function:
    1. Sets the LangChain tracing variables (nothing in this runner is traced:
       the evaluators are plain functions; traces come from the server)
    2. Creates evaluator instances
    3. Scores each test case's expected values against themselves (the
       workflow is NOT run here), which checks your evaluator logic only:
       a correct evaluator prints 1.00 averages by construction
    4. Collects and reports scores
    """
    if not LANGSMITH_API_KEY:
        print("Warning: LANGSMITH_API_KEY not set. Running in local-only mode.")

    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_PROJECT", LANGSMITH_PROJECT)

    def _make(factory):
        try:
            return factory()
        except NotImplementedError:
            return None

    risk_evaluator = _make(create_risk_accuracy_evaluator)
    consistency_evaluator = _make(create_approval_consistency_evaluator)

    print(f"Running evaluation with {len(EVAL_DATASET)} test cases...")
    print(f"LangSmith project: {LANGSMITH_PROJECT}")
    print("=" * 60)

    risk_scores = []
    consistency_scores = []

    evaluators = [
        ("Risk", risk_evaluator, lambda exp: {"risk_level": exp["risk_level"]}, risk_scores),
        ("Consistency", consistency_evaluator, lambda exp: {"status": exp["status"]}, consistency_scores),
    ]

    for i, test_case in enumerate(EVAL_DATASET):
        inputs = test_case["input"]
        expected = test_case["expected"]

        print(f"\nTest case {i + 1}: {inputs['title']}")
        print(f"  Amount: ${inputs['amount']:,.2f}")
        print(f"  Department: {inputs['department']}")
        print(f"  Expected risk: {expected['risk_level']}")
        print(f"  Expected status: {expected['status']}")

        for name, evaluator, make_outputs, scores in evaluators:
            if evaluator is None:
                print(f"  {name} evaluator: NOT IMPLEMENTED")
                continue
            try:
                result = evaluator(
                    inputs=inputs,
                    outputs=make_outputs(expected),
                    reference_outputs=expected,
                )
                scores.append(result.get("score", 0))
                print(f"  {name} evaluator score: {result.get('score', 'N/A')}")
            except NotImplementedError:
                print(f"  {name} evaluator: NOT IMPLEMENTED")
            except Exception as e:
                print(f"  {name} evaluator error: {e}")

    print("\n" + "=" * 60)
    if risk_scores:
        print(f"Average risk accuracy: {sum(risk_scores) / len(risk_scores):.2f}")
    if consistency_scores:
        print(f"Average consistency: {sum(consistency_scores) / len(consistency_scores):.2f}")
    print("Evaluation complete.")


if __name__ == "__main__":
    run_evaluation()
