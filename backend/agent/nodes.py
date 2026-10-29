"""
Node functions for the Financial Approval workflow.

Students implement 8 node functions and 6 routing functions that
form the LangGraph approval pipeline with risk-based escalation.

Part 1: LangGraph Workflow + Interrupts (35 points)
"""

import json

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import interrupt, Command
from backend.agent.state import ApprovalState
from backend.config import (
    get_llm,
    BUDGET_CEILING,
    DEPARTMENT_BUDGETS,
    HIGH_RISK_THRESHOLD,
    MEDIUM_RISK_THRESHOLD,
)
from backend.guardrails.input_validator import validate_request
from backend.guardrails.output_filter import sanitize_output


# ============================================================
# NODE FUNCTIONS (8 total)
# ============================================================

def submit_request(state: ApprovalState) -> dict:
    """
    Node 1: Receive and validate the financial request.

    TODO (3 points):
    - Extract request details from state
    - Call validate_request() to check the request
    - If invalid, set status to "rejected" and return with validation_message
    - If valid, set current_stage to "risk_assessment" and status to "pending"
    - Add an AIMessage summarizing the submitted request
    - Return updated state fields as a dict

    Hints:
    - validate_request() returns (is_valid: bool, message: str)
    - Return dict with keys: is_valid, validation_message, current_stage, status, messages
    - Also reset the previous request's review state ("decisions": [], risk_level /
      manager_approved / finance_approved / final_approved: None, ...): the frontend
      reuses one thread for every request in a chat session, so old values are still in
      the checkpoint (a request rejected here never runs assess_risk, so without the reset
      it would report the previous request's risk_level)
    - Reset department_budget / budget_remaining / within_budget to None, not 0: high and
      critical requests skip validate_budget, and the Approval Panel shows "Not checked"
      only when department_budget is None (0 shows "$0, Within budget")
    """
    raise NotImplementedError("TODO: Implement submit_request node (3 points)")


def assess_risk(state: ApprovalState) -> dict:
    """
    Node 2: Use LLM to assess risk level of the request.

    TODO (3 points):
    - Create a prompt asking the LLM to assess risk as "low", "medium", "high", or "critical"
    - Include the request title, description, amount, department, justification, and priority
      (the "urgent" rule below needs priority)
    - Call get_llm() and invoke it with the prompt
    - Parse the LLM response text to extract risk_level and risk_reasoning
    - Add an AIMessage with the risk assessment
    - Return updated state fields

    Hints:
    - Use response = get_llm().invoke([HumanMessage(content=prompt)])
    - Read the reply with response.text (a property: no parentheses), not response.content.
      Gemini returns content as a list of content blocks, so re.search() or json.loads()
      on response.content raises TypeError, and `"low" in response.content` is silently
      False (every request falls back to "medium"); .text is a plain string for OpenAI
      and Gemini
    - The LLM should return one of: "low", "medium", "high", "critical"
    - Default to "medium" if parsing fails
    - Give the LLM the rules the eval dataset is labelled with
      (backend/evaluation/dataset.py, dataset_generator.py), or Part 4/5 scores drop:
        amount <= $10,000 → low; $10,001-$50,000 → medium;
        $50,001-$100,000 → high; priority "urgent" and amount > $50,000 → critical
    - The route_after_risk router will decide the next step based on risk_level
    - Low risk → budget validation (auto-approve path)
    - Medium/High/Critical → manager review
    """
    raise NotImplementedError("TODO: Implement assess_risk node (3 points)")


def manager_review(state: ApprovalState) -> dict:
    """
    Node 3: Manager review with human-in-the-loop interrupt.

    TODO (3 points):
    - Call interrupt() with a dict containing request details for the manager:
      {"type": "manager_review", "request_id": ..., "title": ..., "amount": ...,
       "department": ..., "risk_level": ..., "risk_reasoning": ...}
    - The interrupt() return value is the manager's decision dict:
      {"approved": bool, "comments": str}
    - Store the decision in manager_approved and manager_comments
    - Record the decision in the decisions list
    - Add an AIMessage with the manager's decision
    - Return updated state fields

    Hints:
    - decision = interrupt({...}) pauses the graph until user responds
    - The frontend sends the decision as a JSON string — use json.loads(decision) if it's a str
    - Append to decisions list: {"stage": "manager_review", "approved": ...,
      "decision": "approved" | "rejected", "reviewer": "Manager", "comments": ...,
      "reasoning": ...}  ("decision" and "reasoning" are the keys the Part 5 audit-trail
      evaluator checks)
    - ApprovalState.decisions has no reducer, so return the whole list:
      {"decisions": state.get("decisions", []) + [entry]}; returning [entry] alone
      overwrites the earlier decisions (same for finance_review and final_signoff)
    - The route_after_manager router decides the next step based on approval + risk_level
    """
    raise NotImplementedError("TODO: Implement manager_review node (3 points)")


def validate_budget(state: ApprovalState) -> dict:
    """
    Node 4: Validate request against department budget.

    TODO (1 point):
    - Look up the department's budget from DEPARTMENT_BUDGETS
    - Check if the requested amount is within budget
    - Set department_budget, budget_remaining, and within_budget
    - Add an AIMessage with budget validation results
    - Return updated state fields

    Hints:
    - budget = DEPARTMENT_BUDGETS.get(state["department"], 0)
    - within_budget = state["amount"] <= budget
    - budget_remaining = budget - state["amount"]
    - The route_after_budget router decides the next step:
      - Within budget → process_request (auto-approve)
      - Over budget + low risk → escalate to manager_review
      - Over budget + medium risk → escalate to finance_review
    """
    raise NotImplementedError("TODO: Implement validate_budget node (1 point)")


def finance_review(state: ApprovalState) -> dict:
    """
    Node 5: Finance team review with human-in-the-loop interrupt.

    TODO (3 points):
    - Call interrupt() with a dict for finance review:
      {"type": "finance_review", "request_id": ..., "title": ..., "amount": ...,
       "department": ..., "risk_level": ..., "within_budget": ...,
       "department_budget": ..., "budget_remaining": ..., "manager_comments": ...}
    - Store the decision in finance_approved and finance_comments
    - Record the decision in the decisions list
    - Add an AIMessage with finance decision
    - Return updated state fields

    Hints:
    - The route_after_finance router decides the next step:
      - Rejected → handle_rejection
      - Approved + high risk → process_request (done)
      - Approved + critical risk → final_signoff (one more review)
      - Approved + medium risk (over-budget escalation) → process_request
    """
    raise NotImplementedError("TODO: Implement finance_review node (3 points)")


def final_signoff(state: ApprovalState) -> dict:
    """
    Node 6: Executive final sign-off with human-in-the-loop interrupt.

    TODO (3 points):
    - Call interrupt() with a dict summarizing the full approval chain:
      {"type": "final_signoff", "request_id": ..., "title": ..., "amount": ...,
       "department": ..., "risk_level": ..., "manager_approved": ...,
       "finance_approved": ..., "within_budget": ..., "decisions": ...}
    - Store the decision in final_approved and final_comments
    - Set current_stage to "processing" if approved, else "rejection"
    - Record the decision in the decisions list
    - Add an AIMessage with final decision
    - Return updated state fields
    """
    raise NotImplementedError("TODO: Implement final_signoff node (3 points)")


def process_request(state: ApprovalState) -> dict:
    """
    Node 7: Process the fully-approved request.

    TODO (1 point):
    - Set status to "approved"
    - Set current_stage to "complete"
    - Create a summary message listing all approval stages and comments
    - Call sanitize_output() on the summary before adding to messages
    - Return updated state fields

    Hints:
    - sanitize_output() filters PII from the output text
    """
    raise NotImplementedError("TODO: Implement process_request node (1 point)")


def handle_rejection(state: ApprovalState) -> dict:
    """
    Node 8: Handle a rejected request.

    TODO (2 points):
    - Set status to "rejected"
    - Set current_stage to "complete"
    - Determine which stage rejected the request from the decisions list
    - Create a rejection summary with the rejection reason
    - Call sanitize_output() on the summary
    - Add an AIMessage with the rejection details
    - Return updated state fields
    """
    raise NotImplementedError("TODO: Implement handle_rejection node (2 points)")


# ============================================================
# ROUTING FUNCTIONS (6 total — implement the escalation logic)
# ============================================================

def route_after_submission(state: ApprovalState) -> str:
    """
    Router: After submit_request, go to risk assessment or rejection.

    TODO (1 point):
    - Return "assess_risk" if state["is_valid"] is True
    - Return "handle_rejection" otherwise
    """
    raise NotImplementedError("TODO: Implement route_after_submission (1 point)")


def route_after_risk(state: ApprovalState) -> str:
    """
    Router: After assess_risk, route based on risk level.

    This is the core escalation entry point. Low-risk requests skip
    human review and go directly to budget validation (auto-approve path).
    All other risk levels require manager review first.

    TODO (1 point):
    - Return "validate_budget" if risk_level is "low"
    - Return "manager_review" for "medium", "high", or "critical"

    Hints:
    - state["risk_level"] contains the assessed risk level
    - Low risk = auto-approve path (no human review needed if within budget)
    """
    raise NotImplementedError("TODO: Implement route_after_risk (1 point)")


def route_after_manager(state: ApprovalState) -> str:
    """
    Router: After manager_review, route based on approval + risk level.

    The next step depends on BOTH the manager's decision AND the risk level:
    - Rejected → handle_rejection (any risk level)
    - Approved + low risk (over-budget escalation) → process_request
    - Approved + medium risk → validate_budget
    - Approved + high/critical risk → finance_review

    TODO (1 point):
    - Return "handle_rejection" if state["manager_approved"] is not True
    - Return "process_request" if risk_level is "low" (was escalated from over-budget)
    - Return "validate_budget" if risk_level is "medium"
    - Return "finance_review" if risk_level is "high" or "critical"

    Hints:
    - Low-risk requests only reach manager_review when they are over budget.
      The manager already approved, so we can proceed to processing.
    - Medium-risk requests need budget validation after manager approval.
    - High/critical-risk requests skip budget check and go to finance.
    """
    raise NotImplementedError("TODO: Implement route_after_manager (1 point)")


def route_after_budget(state: ApprovalState) -> str:
    """
    Router: After validate_budget, route based on budget status + risk level.

    Within-budget requests proceed to processing (auto-approved).
    Over-budget requests escalate to the next human reviewer.

    TODO (1 point):
    - Return "process_request" if state["within_budget"] is True
    - If over budget:
      - Return "manager_review" if risk_level is "low" (needs human review)
      - Return "finance_review" if risk_level is "medium" (manager already approved)

    Hints:
    - Low-risk over-budget: first time seeing a human → escalate to manager
    - Medium-risk over-budget: manager already approved → escalate to finance
    - High/critical-risk requests don't go through this router (they skip budget check)
    """
    raise NotImplementedError("TODO: Implement route_after_budget (1 point)")


def route_after_finance(state: ApprovalState) -> str:
    """
    Router: After finance_review, route based on approval + risk level.

    The next step depends on BOTH finance's decision AND the risk level:
    - Rejected → handle_rejection
    - Approved + critical risk → final_signoff (one more review)
    - Approved + any other risk → process_request (done)

    TODO (1 point):
    - Return "handle_rejection" if state["finance_approved"] is not True
    - Return "final_signoff" if risk_level is "critical"
    - Return "process_request" otherwise
    """
    raise NotImplementedError("TODO: Implement route_after_finance (1 point)")


def route_after_final(state: ApprovalState) -> str:
    """
    Router: After final_signoff, go to processing or rejection.

    TODO (1 point):
    - Return "process_request" if state["final_approved"] is True
    - Return "handle_rejection" otherwise
    """
    raise NotImplementedError("TODO: Implement route_after_final (1 point)")
