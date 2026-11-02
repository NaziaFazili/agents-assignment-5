"""
Three-Layer Evaluation Framework for the Financial Approval System.

Students implement evaluator factory functions across three layers:
  Layer 1 — Business Metrics (heuristic, 10 pts)
  Layer 2 — Agent Performance (RAGAS metrics, 12 pts)
  Layer 3 — Safety & Compliance (RAGAS + heuristic, 12 pts)

Each factory returns a callable that takes LangSmith-style arguments
(inputs, outputs, reference_outputs) and returns {"score", "reasoning"}:
    def evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
        return {"score": float, "reasoning": str}
run_three_layer_eval.py calls them directly, on your machine. Keep this return
format: the tests and the runner read it. (langsmith.evaluate() would not accept
it as is: it expects "comment" instead of "reasoning".)

Part 5: Three-Layer Evaluation Framework (34 points)
"""

# ---------------------------------------------------------------------------
# RAGAS imports — Layer 2 uses these directly, Layer 3 optionally
# (ragas==0.4.3, pinned in requirements.txt). ToolCallAccuracy,
# AgentGoalAccuracyWithReference and TopicAdherenceScore are multi-turn
# metrics: score them with `await metric.multi_turn_ascore(MultiTurnSample(...))`.
# Importing from ragas.metrics prints a DeprecationWarning; ignore it. The
# ragas.metrics.collections versions do not accept LangchainLLMWrapper.
# LangchainLLMWrapper(get_llm()) also warns "LangchainLLMWrapper is deprecated
# ... Use llm_factory instead". That warning is expected: keep the wrapper. It
# wraps whatever get_llm() returns (tested with Gemini), while llm_factory needs
# a raw provider client instead of get_llm().
# ---------------------------------------------------------------------------
import asyncio

from ragas.dataset_schema import MultiTurnSample, SingleTurnSample
from ragas.integrations.langgraph import convert_to_ragas_messages
from ragas.llms import LangchainLLMWrapper
from ragas.messages import AIMessage, HumanMessage, ToolCall
from ragas.metrics import (
    AgentGoalAccuracyWithReference,
    Faithfulness,  # Layer 3 hallucination detection
    ToolCallAccuracy,
    TopicAdherenceScore,
)

from backend.config import get_llm

#
# Build any metric that needs an LLM (get_llm()) INSIDE the returned evaluator,
# not in the factory: the tests call every factory, and get_llm() raises
# "Missing credentials" when OPENAI_API_KEY is not set at all (a fresh clone
# without .env, or CI).

# ---------------------------------------------------------------------------
# Helper constants
# ---------------------------------------------------------------------------
RISK_LEVELS = ["low", "medium", "high", "critical"]

EXPECTED_REVIEWS_BY_RISK = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}

BUDGET_CEILING = 100_000

# Human review stages: the only nodes that append to state["decisions"]
HUMAN_REVIEW_STAGES = ["manager_review", "finance_review", "final_signoff"]

# Allowed topics for TopicAdherenceScore. The metric extracts the topics of the
# Human message (the request) and checks each one against this list, so it has
# to cover what a request is about (a purchase such as "Team Lunch"), not only
# the workflow.
REFERENCE_TOPICS = [
    "financial approval request",
    "purchase or business expense of any kind (for example supplies, equipment, "
    "software, servers, events, meals, marketing, travel)",
    "business justification for a purchase",
    "department budget",
    "risk assessment",
    "request validation",
    "approval or rejection decision",
]


# ═══════════════════════════════════════════════════════════════════════════
# Layer 1 — Business Metrics (heuristic evaluators, 10 points)
# ═══════════════════════════════════════════════════════════════════════════


def create_approval_path_evaluator():
    """
    Create an evaluator that checks whether the approval path is correct.


    - Return a callable with signature:
        def evaluator(inputs, outputs, reference_outputs) -> dict
    - Compare outputs["approval_path"] to reference_outputs["approval_path"]
    - Scoring:
        - Exact match (same stages in same order) → 1.0
        - Same number of stages but different order/content → 0.5
        - Different number of stages → 0.0
    - Return {"score": float, "reasoning": str}

    Example:
        outputs = {"approval_path": ["submit_request", "assess_risk", "process_request"]}
        reference_outputs = {"approval_path": ["submit_request", "assess_risk", "process_request"]}
        → {"score": 1.0, "reasoning": "Approval path matches exactly"}

    Returns:
        A callable evaluator function
    """

    def evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
        actual = outputs.get("approval_path", [])
        expected = reference_outputs.get("approval_path", [])

        if actual == expected:
            return {"score": 1.0, "reasoning": "Approval path matches exactly"}

        if len(actual) == len(expected):
            return {
                "score": 0.5,
                "reasoning": "Same number of stages but different path",
            }

        return {"score": 0.0, "reasoning": "Different number of stages"}

    return evaluator


def create_false_positive_evaluator():
    """
    Create an evaluator that detects false positives (approved when should be rejected).


    - Return a callable with signature:
        def evaluator(inputs, outputs, reference_outputs) -> dict
    - A false positive occurs when:
        - reference_outputs["status"] == "rejected" (should be rejected)
        - BUT outputs["status"] == "approved" (was approved instead)
    - Scoring:
        - False positive detected → 0.0 (bad — system approved something it shouldn't have)
        - No false positive → 1.0 (good)
    - Return {"score": float, "reasoning": str}

    Returns:
        A callable evaluator function
    """

    def evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
        actual = outputs.get("status")
        expected = reference_outputs.get("status")

        if expected == "rejected" and actual == "approved":
            return {
                "score": 0.0,
                "reasoning": "False positive: Request was incorrectly approved",
            }

        return {"score": 1.0, "reasoning": "No false positive detected"}

    return evaluator


def create_false_negative_evaluator():
    """
    Create an evaluator that detects false negatives (rejected when should be approved).

    - Return a callable with signature:
        def evaluator(inputs, outputs, reference_outputs) -> dict
    - A false negative occurs when:
        - reference_outputs["status"] == "approved" (should be approved)
        - BUT outputs["status"] == "rejected" (was rejected instead)
    - Scoring:
        - False negative detected → 0.0 (bad — system rejected something it shouldn't have)
        - No false negative → 1.0 (good)
    - Return {"score": float, "reasoning": str}

    Returns:
        A callable evaluator function
    """

    def evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:

        actual = outputs.get("status")
        expected = reference_outputs.get("status")

        if expected == "approved" and actual == "rejected":
            return {
                "score": 0.0,
                "reasoning": "False negative: Request was incorrectly rejected",
            }

        return {"score": 1.0, "reasoning": "No false negative detected"}

    return evaluator


def create_human_review_efficiency_evaluator():
    """
    Create an evaluator that checks human review count accuracy.


    - Return a callable with signature:
        def evaluator(inputs, outputs, reference_outputs) -> dict
    - Compare the number of human reviews in outputs to expected:
        actual = outputs["human_reviews"]  (int — number of human reviews performed)
        expected = reference_outputs["human_reviews"]  (int — expected count)
    - Scoring:
        - Exact match → 1.0
        - Off by 1 → 0.5
        - Off by more than 1 → 0.0
    - Return {"score": float, "reasoning": str}

    Returns:
        A callable evaluator function
    """

    def evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:

        actual = outputs.get("human_reviews", 0)
        expected = reference_outputs.get("human_reviews", 0)

        difference = abs(actual - expected)

        if difference == 0:
            return {"score": 1.0, "reasoning": "Human review count matches exactly"}

        if difference == 1:
            return {"score": 0.5, "reasoning": "Human review count is off by 1"}

        return {"score": 0.0, "reasoning": "Human review count differs by more than 1"}

    return evaluator


# ═══════════════════════════════════════════════════════════════════════════
# Layer 2 — Agent Performance (RAGAS metrics, 12 points)
# ═══════════════════════════════════════════════════════════════════════════


def create_tool_call_accuracy_evaluator():
    """
    Create an evaluator that uses RAGAS ToolCallAccuracy to validate workflow stages.

    - Return a callable with signature:
        def evaluator(inputs, outputs, reference_outputs) -> dict

    - Steps to implement:
      1. Import and instantiate ragas.metrics.ToolCallAccuracy (no LLM needed)
      2. Convert approval_path stages to RAGAS ToolCall format:
         Each stage in outputs["approval_path"] becomes a ToolCall(name=stage, args={})
         (ToolCall from ragas.messages)
      3. Similarly convert reference_outputs["approval_path"] to reference ToolCalls
      4. Create a MultiTurnSample:
           user_input=[HumanMessage(content=<request summary>),
                       AIMessage(content=<final status>, tool_calls=<actual ToolCalls>)]
           reference_tool_calls=<reference ToolCalls>
      5. Score with asyncio.run(metric.multi_turn_ascore(sample))
         (ToolCallAccuracy is a multi-turn metric; it has no single_turn_ascore)
      6. Return {"score": float, "reasoning": str}

    - Alternatively, if RAGAS is not installed, fall back to a simple
      comparison of approval_path lists (partial credit approach).

    Returns:
        A callable evaluator function
    """

    def evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:

        actual_path = outputs.get("approval_path", [])
        expected_path = reference_outputs.get("approval_path", [])

        # Convert workflow stages into RAGAS ToolCalls
        actual_calls = [ToolCall(name=stage, args={}) for stage in actual_path]

        expected_calls = [ToolCall(name=stage, args={}) for stage in expected_path]

        # Create a request summary
        request_summary = f"Financial approval request for ${inputs.get('amount', 0)} "

        # Create a MultiTurnSample
        sample = MultiTurnSample(
            user_input=[
                HumanMessage(content=request_summary),
                AIMessage(
                    content=f"Request {outputs.get('status', 'unknown')}",
                    tool_calls=actual_calls,
                ),
            ],
            reference_tool_calls=expected_calls,
        )

        # Evaluate tool-call accuracy
        metric = ToolCallAccuracy()
        score = asyncio.run(metric.multi_turn_ascore(sample))

        return {
            "score": float(score),
            "reasoning": f"RAGAS tool-call accuracy score: {score:.2f}",
        }

    return evaluator


def create_agent_goal_accuracy_evaluator():
    """
    Create an evaluator using RAGAS AgentGoalAccuracyWithReference.

    - Return a callable with signature:
        def evaluator(inputs, outputs, reference_outputs) -> dict

    - Steps to implement:
      1. Import ragas.metrics.AgentGoalAccuracyWithReference
      2. The "goal" is whether the agent reached the correct final status:
         - outputs["status"] should match reference_outputs["status"]
         - The reasoning/justification should align with the decision
      3. Construct a MultiTurnSample with:
         - user_input: a list of ragas messages, e.g.
             [HumanMessage(content=<request description from inputs>),
              AIMessage(content=<agent's final status and reasoning from outputs>)]
           (MultiTurnSample has no `response` field; the agent's answer goes in
            user_input as an AIMessage)
         - reference: the expected outcome as a string, e.g. "Request is approved"
      4. Score with asyncio.run(metric.multi_turn_ascore(sample))
      5. Return {"score": float, "reasoning": str}

    - Hint: This metric uses an LLM judge. Create it inside the evaluator:
        from ragas.llms import LangchainLLMWrapper
        metric = AgentGoalAccuracyWithReference(llm=LangchainLLMWrapper(get_llm()))

    Returns:
        A callable evaluator function
    """

    def evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:

        sample = MultiTurnSample(
            user_input=[
                HumanMessage(content=inputs.get("description", "")),
                AIMessage(
                    content=f"Status: {outputs.get('status')}. "
                    f"Reasoning: {outputs.get('reasoning', '')}"
                ),
            ],
            reference=f"Request is {reference_outputs.get('status')}",
        )

        # Create the LLM judge inside the evaluator
        metric = AgentGoalAccuracyWithReference(llm=LangchainLLMWrapper(get_llm()))

        score = asyncio.run(metric.multi_turn_ascore(sample))

        return {
            "score": float(score),
            "reasoning": f"Agent goal accuracy score: {score:.2f}",
        }

    return evaluator


def create_topic_adherence_evaluator():
    """
    Create an evaluator using RAGAS TopicAdherenceScore.


    - Return a callable with signature:
        def evaluator(inputs, outputs, reference_outputs) -> dict

    - Steps to implement:
      1. Import ragas.metrics.TopicAdherenceScore
      2. The allowed topics are REFERENCE_TOPICS (given above)
      3. The metric extracts the topics of the Human message, asks the judge whether
         the AI answered each one, and in "precision" mode scores the share of
         answered topics that fall inside REFERENCE_TOPICS. An agent that answers an
         off-topic message (a recipe request, say) scores low. It does not grade
         extra text the AI adds on its own.
      4. Construct a MultiTurnSample with
         user_input=[HumanMessage(<request summary>), AIMessage(<agent text>)]
         and reference_topics=REFERENCE_TOPICS. Build the request summary from
         title, description, amount, department, priority and justification, and
         leave out request_id: the judge extracts "Request EVAL-004" as a topic
         and marks it off-topic.
      5. Score with asyncio.run(metric.multi_turn_ascore(sample))
      6. Return {"score": float, "reasoning": str}

    - Hint: reference_topics belongs to the sample, not the metric. Create the
      metric inside the evaluator:
        metric = TopicAdherenceScore(llm=LangchainLLMWrapper(get_llm()), mode="precision")
        sample = MultiTurnSample(
            user_input=[...],
            reference_topics=REFERENCE_TOPICS,
        )

    Returns:
        A callable evaluator function
    """

    def evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:

        request = (
            f"Title: {inputs.get('title', '')}. "
            f"Description: {inputs.get('description', '')}. "
            f"Amount: {inputs.get('amount', '')}. "
            f"Department: {inputs.get('department', '')}. "
            f"Priority: {inputs.get('priority', '')}. "
            f"Justification: {inputs.get('justification', '')}"
        )

        response = (
            f"Status: {outputs.get('status', '')}. "
            f"Reasoning: {outputs.get('reasoning', '')}"
        )

        sample = MultiTurnSample(
            user_input=[HumanMessage(content=request), AIMessage(content=response)],
            reference_topics=REFERENCE_TOPICS,
        )

        metric = TopicAdherenceScore(
            llm=LangchainLLMWrapper(get_llm()), mode="precision"
        )

        score = asyncio.run(metric.multi_turn_ascore(sample))

        return {
            "score": float(score),
            "reasoning": f"Topic adherence score: {score:.2f}",
        }

    return evaluator


# ═══════════════════════════════════════════════════════════════════════════
# Layer 3 — Safety & Compliance (RAGAS + heuristic, 12 points)
# ═══════════════════════════════════════════════════════════════════════════


def create_policy_adherence_evaluator():
    """
    Create an evaluator that checks policy compliance with heuristic rules.

    - Return a callable with signature:
        def evaluator(inputs, outputs, reference_outputs) -> dict
    - Policy rules to check:
      1. Amounts exceeding BUDGET_CEILING ($100,000) MUST be rejected
      2. Approved requests must have AT LEAST the required number of human
         reviews based on risk level (use EXPECTED_REVIEWS_BY_RISK dict):
           - low: 0 reviews, medium: 1, high: 2, critical: 3
         Use >=, not ==: an over-budget request gets an extra review from the
         budget escalation (EVAL-011 is low risk with 1 review, EVAL-012 is
         medium risk with 2), and that still follows policy.
         (only look this up for approved requests: risk_level is None when a
         request is rejected at submit_request)
      3. Negative amounts MUST be rejected
    - Scoring:
        - All policy rules satisfied → 1.0
        - Some rules violated → fraction of rules passed (e.g., 2/3 ≈ 0.67)
    - Return {"score": float, "reasoning": str}

    Returns:
        A callable evaluator function
    """

    def evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:

        amount = inputs.get("amount", 0)
        status = outputs.get("status")
        risk = outputs.get("risk_level")
        reviews = outputs.get("human_reviews", 0)

        passed = 0

        # Requests over $100,000 must be rejected
        if amount > BUDGET_CEILING:
            if status == "rejected":
                passed += 1
        else:
            passed += 1

        # Approved requests need enough human reviews
        if status == "approved":
            required_reviews = EXPECTED_REVIEWS_BY_RISK[risk]

            if reviews >= required_reviews:
                passed += 1
        else:
            passed += 1

        # Negative amounts must be rejected
        if amount < 0:
            if status == "rejected":
                passed += 1
        else:
            passed += 1

        return {
            "score": passed / 3,
            "reasoning": f"{passed} out of 3 policy rules satisfied",
        }

    return evaluator


def create_hallucination_evaluator():
    """
    Create an evaluator that detects hallucinations in agent output.


    - Return a callable with signature:
        def evaluator(inputs, outputs, reference_outputs) -> dict

    - Choose ONE approach:

      Option A — RAGAS Faithfulness:
        1. Import ragas.metrics.Faithfulness
        2. Check if the agent's text (status, risk level, stages, decision
           reasoning) is grounded in the request and in what the workflow recorded
        3. Faithfulness is single-turn: build
             SingleTurnSample(
                 user_input=<request summary>,
                 response=<agent text>,
                 retrieved_contexts=[
                     <input fields as text>,
                     <workflow record as text: status, risk_level, approval_path,
                      human_reviews, and each decision's stage and decision>,
                 ],
             )
           and score with asyncio.run(metric.single_turn_ascore(sample)).
           The judge marks every statement it cannot find in retrieved_contexts as
           unsupported. With the input fields alone, true statements about the
           result ("Final status: approved") count as hallucinations and a correct
           solution scores near 0. Leave the free-text reasoning out of the record,
           so made-up reasons in the agent text still count against it.

      Option B — Direct LLM judge:
        1. Use get_llm() to create an LLM
        2. Prompt it to check if outputs contain any fabricated details
           not present in the inputs (e.g., invented policy numbers,
           made-up approval histories, fabricated budget figures)
        3. Parse the LLM response text into a score (response.text, not
           response.content: Gemini returns content as a list of content blocks)

    - Return {"score": float, "reasoning": str}
      Score 1.0 = no hallucinations detected, 0.0 = hallucinations found

    Returns:
        A callable evaluator function
    """

    def evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:

        # Original request
        request = (
            f"Title: {inputs.get('title', '')}. "
            f"Description: {inputs.get('description', '')}. "
            f"Amount: {inputs.get('amount', '')}. "
            f"Department: {inputs.get('department', '')}. "
            f"Priority: {inputs.get('priority', '')}. "
            f"Justification: {inputs.get('justification', '')}"
        )
        # Actual workflow record
        record = (
            f"Status: {outputs.get('status')}. "
            f"Risk level: {outputs.get('risk_level')}. "
            f"Approval path: {outputs.get('approval_path', [])}. "
            f"Human reviews: {outputs.get('human_reviews', 0)}. "
        )

        for decision in outputs.get("decisions", []):
            record += (
                f"Review stage: {decision.get('stage')}. "
                f"Decision: {decision.get('decision')}. "
            )

        # Agent's response
        response = (
            f"Final status: {outputs.get('status')}. "
            f"Risk level: {outputs.get('risk_level')}. "
            f"Stages: {outputs.get('approval_path', [])}. "
            f"Decision reasoning: {outputs.get('reasoning', '')}"
        )

        sample = SingleTurnSample(
            user_input=request, response=response, retrieved_contexts=[request, record]
        )

        metric = Faithfulness(llm=LangchainLLMWrapper(get_llm()))

        score = asyncio.run(metric.single_turn_ascore(sample))

        return {"score": float(score), "reasoning": f"Faithfulness score: {score:.2f}"}

    return evaluator


def create_audit_trail_evaluator():
    """
    Create an evaluator that validates the completeness of the audit trail.

    - Return a callable with signature:
        def evaluator(inputs, outputs, reference_outputs) -> dict
    - Only the human review nodes (manager_review, finance_review, final_signoff)
      append to state["decisions"] (see the manager_review hints in nodes.py), so
      count human review stages only. Expected count = len(reference_outputs["decisions"])
      if present, otherwise the number of HUMAN_REVIEW_STAGES in
      reference_outputs["approval_path"] (the eval dataset has no "decisions" key;
      run_three_layer_eval builds one entry per human review stage)
    - Check the following in outputs["decisions"]:
      1. decisions is non-empty when the expected count is above 0 (an empty list is
         correct when it is 0: auto-approved, or rejected at submit_request)
      2. Each decision entry has required keys: "stage", "decision", "reasoning"
      3. Number of decision entries equals the expected count
    - Scoring:
        - Score = fraction of checks that pass (3 checks total)
        - All pass → 1.0, two pass → 0.67, one passes → 0.33, none → 0.0
    - Return {"score": float, "reasoning": str}

    Example:
        outputs = {
            "decisions": [
                {"stage": "manager_review", "decision": "approved", "reasoning": "..."},
                {"stage": "finance_review", "decision": "approved", "reasoning": "..."},
            ]
        }
        reference_outputs = {"approval_path": ["submit_request", "assess_risk",
            "manager_review", "finance_review", "process_request"]}
        → expected count 2: non-empty (pass), keys present (pass), count matches (pass) → 1.0
        An auto-approved request (no review stage in the path) with decisions [] → 1.0

    Returns:
        A callable evaluator function
    """

    def evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:

        decisions = outputs.get("decisions", [])

        # Get expected number of human reviews
        if "decisions" in reference_outputs:
            expected_count = len(reference_outputs["decisions"])
        else:
            expected_path = reference_outputs.get("approval_path", [])
            expected_count = sum(
                1 for stage in expected_path if stage in HUMAN_REVIEW_STAGES
            )

        passed = 0

        # Decisions exist when reviews are expected
        if expected_count == 0 or (expected_count > 0 and len(decisions) > 0):
            passed += 1

        # Every decision contains required keys
        required_keys = {"stage", "decision", "reasoning"}

        has_required_keys = True

        for decision in decisions:
            if not required_keys.issubset(decision):
                has_required_keys = False
                break

        if has_required_keys:
            passed += 1

        # Check 3: Number of decisions matches expected count
        if len(decisions) == expected_count:
            passed += 1

        return {
            "score": round(passed / 3, 2),
            "reasoning": f"{passed} out of 3 audit trail checks passed",
        }

    return evaluator
