"""
Custom LangSmith evaluators for the Financial Approval System.

Students implement evaluator factory functions that return callables
taking LangSmith-style arguments (inputs, outputs, reference_outputs).
run_eval.py calls them directly, on your machine; nothing is sent to LangSmith.
(If you later pass them to langsmith.evaluate(), give each inner function its
own name: LangSmith uses the function name as the feedback key.)

Part 4: LangSmith Tracing + Evaluation (20 points)
"""


def create_risk_accuracy_evaluator():
    """
    Create an evaluator that checks risk assessment accuracy.

    TODO (10 points):
    - Return a callable (function) that takes two arguments:
        - inputs: dict with "amount", "department", "description"
        - outputs: dict with "risk_level"
    - The callable should also accept a keyword argument:
        - reference_outputs: dict with expected "risk_level"
    - The evaluator logic:
        - Compare outputs["risk_level"] with reference_outputs["risk_level"]
        - Return {"score": 1.0} if they match exactly
        - Return {"score": 0.5} if they are adjacent levels
          (e.g., "low"/"medium", "medium"/"high", "high"/"critical")
        - Return {"score": 0.0} otherwise
    - Adjacent levels: define an ordered list ["low", "medium", "high", "critical"]
      and check if the absolute index difference is 1
    - risk_level can be None: requests rejected at submit_request never run
      assess_risk (EVAL-007, EVAL-008, EVAL-010). Check the exact match first, so
      None vs None scores 1.0, and score 0.0 when only one side is None
      (list.index(None) raises ValueError)

    Returns:
        A callable evaluator function
    """
    raise NotImplementedError("TODO: Implement create_risk_accuracy_evaluator (10 points)")


def create_approval_consistency_evaluator():
    """
    Create an evaluator that checks approval decision consistency.

    TODO (10 points):
    - Return a callable that takes:
        - inputs: dict with "amount", "department"
        - outputs: dict with "status" (approved/rejected)
    - The callable should also accept a keyword argument:
        - reference_outputs: dict with expected "status"
    - The evaluator logic:
        - Return {"score": 1.0} if outputs["status"] matches reference_outputs["status"]
        - Return {"score": 0.0} otherwise

    Returns:
        A callable evaluator function
    """
    raise NotImplementedError("TODO: Implement create_approval_consistency_evaluator (10 points)")
