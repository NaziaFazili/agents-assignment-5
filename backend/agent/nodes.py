"""
Node functions for the Financial Approval workflow.

Students implement 8 node functions and 6 routing functions that
form the LangGraph approval pipeline with risk-based escalation.

Part 1: LangGraph Workflow + Interrupts (35 points)
"""

import json

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Command, interrupt

from backend.agent.state import ApprovalState
from backend.config import (
    BUDGET_CEILING,
    DEPARTMENT_BUDGETS,
    HIGH_RISK_THRESHOLD,
    MEDIUM_RISK_THRESHOLD,
    get_llm,
)
from backend.guardrails.input_validator import validate_request
from backend.guardrails.output_filter import sanitize_output

# ============================================================
# NODE FUNCTIONS (8 total)
# ============================================================


def submit_request(state: ApprovalState) -> dict:
    """
    Node 1: Receive and validate the financial request.

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

    # Extract request details from state
    request_id = state.get("request_id", "")
    title = state.get("title", "Untitled Request")
    description = state.get("description", "No description")
    amount = state.get("amount", 0)
    department = state.get("department", "unknown")
    justification = state.get("justification", "No justification")

    # Validate the request
    # is_valid, validation_message = validate_request(state)
    is_valid, validation_message = validate_request(
        amount,
        department,
        title,
        description,
        justification,
    )

    #  is_valid, validation_message, current_stage, status, messages
    return {
        # Validation results
        "is_valid": is_valid,
        "validation_message": validation_message,
        # Workflow status If valid, set current_stage to "risk_assessment" and status to "pending"
        # If invalid, set status to "rejected" and return with validation_message
        "current_stage": "risk_assessment" if is_valid else "validation",
        "status": "pending" if is_valid else "rejected",
        # Conversation message
        "messages": [
            AIMessage(
                content=(
                    f"Request {request_id} submitted successfully."
                    if is_valid
                    else f"Request rejected: {validation_message}"
                )
            )
        ],
        # Reset previous request's state
        "risk_level": None,
        "risk_reasoning": "",
        "manager_approved": None,
        "manager_comments": "",
        "finance_approved": None,
        "finance_comments": "",
        "final_approved": None,
        "final_comments": "",
        "department_budget": None,
        "budget_remaining": None,
        "within_budget": None,
        "decisions": [],
    }


def assess_risk(state: ApprovalState) -> dict:
    """
    Node 2: Use LLM to assess risk level of the request.

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
    title = state.get("title", "")
    description = state.get("description", "")
    amount = state.get("amount", 0)
    department = state.get("department", "")
    justification = state.get("justification", "")
    priority = state.get("priority", "")

    # Build risk assessment prompt
    prompt = f"""
    You are a financial risk assessment assistant.

    Assess the risk level of the following financial request.

    Request Details:
    - Title: {title}
    - Description: {description}
    - Amount: ${amount}
    - Department: {department}
    - Justification: {justification}
    - Priority: {priority}

    Risk Classification Rules:
    1. Amount <= $10,000: low
    2. Amount > $10,000 and <= $50,000: medium
    3. Amount > $50,000 and <= $100,000: high
    4. Priority is "urgent" and amount > $50,000: critical

    Apply the urgent priority rule first.

    Return ONLY valid JSON in this format:
    {{
        "risk_level": "low",
        "risk_reasoning": "Explanation of the risk assessment"
    }}

    The risk_level must be one of: low, medium, high, critical.
    
    """
    response = get_llm().invoke([HumanMessage(content=prompt)])

    # Default values
    risk_level = "medium"
    risk_reasoning = "Unable to determine risk level from LLM response."

    try:
        result = json.loads(response.text.strip())
        risk_level = result.get("risk_level", "medium")
        risk_reasoning = result.get("risk_reasoning", "")

        if risk_level not in ["low", "medium", "high", "critical"]:
            risk_level = "medium"
    except (json.JSONDecodeError, TypeError, ValueError):
        risk_level = "medium"
        risk_reasoning = "Unable to parse LLM risk assessment."

    return {
        "risk_level": risk_level,
        "risk_reasoning": risk_reasoning,
        "messages": [
            AIMessage(content=f"Risk Level: {risk_level}\nReasoning: {risk_reasoning}")
        ],
    }


def manager_review(state: ApprovalState) -> dict:
    """
    Node 3: Manager review with human-in-the-loop interrupt.


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
    # Pause workflow and request manager approval
    decision = interrupt(
        {
            "type": "manager_review",
            "request_id": state.get("request_id"),
            "title": state.get("title", ""),
            "amount": state.get("amount"),
            "department": state.get("department", ""),
            "risk_level": state.get("risk_level"),
            "risk_reasoning": state.get("risk_reasoning"),
        }
    )

    # Frontend may return the decision as a JSON string
    if isinstance(decision, str):
        decision = json.loads(decision)

    # Extract manager's decision
    approved = decision.get("approved", False)
    comments = decision.get("comments", "")

    decision_status = "approved" if approved else "rejected"

    # Create audit trail entry
    entry = {
        "stage": "manager_review",
        "approved": approved,
        "decision": decision_status,
        "reviewer": "Manager",
        "comments": comments,
        "reasoning": comments or f"Manager {decision_status} the request.",
    }

    # Return updated state fields
    return {
        "manager_approved": approved,
        "manager_comments": comments,
        "decisions": state.get("decisions", []) + [entry],
        "messages": [
            AIMessage(
                content=f"Manager {decision_status} the request. Comments: {comments}"
            )
        ],
    }


def validate_budget(state: ApprovalState) -> dict:
    """
    Node 4: Validate request against department budget.


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
    # Get request details for department and amount
    department = state.get("department", "")
    amount = state.get("amount", 0)

    # Look up department budget
    budget = DEPARTMENT_BUDGETS.get(department, 0)

    # Validate budget
    within_budget = amount <= budget
    budget_remaining = budget - amount

    # Create validation message
    if within_budget:
        message = (
            f"Budget validation passed. Remaining budget: ${budget_remaining:,.2f}"
        )
    else:
        message = f"Budget validation failed. Request exceeds the budget by ${abs(budget_remaining):,.2f}"

    # Return updated state fields
    return {
        "department_budget": budget,
        "budget_remaining": budget_remaining,
        "within_budget": within_budget,
        "messages": [AIMessage(content=message)],
    }


def finance_review(state: ApprovalState) -> dict:
    """
    Node 5: Finance team review with human-in-the-loop interrupt.

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
    # Pause workflow for finance team review
    decision = interrupt(
        {
            "type": "finance_review",
            "request_id": state.get("request_id"),
            "title": state.get("title"),
            "amount": state.get("amount"),
            "department": state.get("department"),
            "risk_level": state.get("risk_level"),
            "within_budget": state.get("within_budget"),
            "department_budget": state.get("department_budget"),
            "budget_remaining": state.get("budget_remaining"),
            "manager_comments": state.get("manager_comments"),
        }
    )

    # Convert JSON string to dictionary
    if isinstance(decision, str):
        decision = json.loads(decision)

    # Extract finance team's decision
    approved = decision.get("approved", False)
    comments = decision.get("comments", "")

    decision_status = "approved" if approved else "rejected"

    # Create audit trail entry
    entry = {
        "stage": "finance_review",
        "approved": approved,
        "decision": decision_status,
        "reviewer": "Finance",
        "comments": comments,
        "reasoning": comments or f"Finance {decision_status} the request.",
    }

    # Return updated state fields
    return {
        "finance_approved": approved,
        "finance_comments": comments,
        "decisions": state.get("decisions", []) + [entry],
        "messages": [
            AIMessage(
                content=f"Finance {decision_status} the request. Comments: {comments}"
            )
        ],
    }


def final_signoff(state: ApprovalState) -> dict:
    """
    Node 6: Executive final sign-off with human-in-the-loop interrupt.


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

    # Pause workflow for executive approval
    decision = interrupt(
        {
            "type": "final_signoff",
            "request_id": state.get("request_id"),
            "title": state.get("title"),
            "amount": state.get("amount"),
            "department": state.get("department"),
            "risk_level": state.get("risk_level"),
            "manager_approved": state.get("manager_approved"),
            "finance_approved": state.get("finance_approved"),
            "within_budget": state.get("within_budget"),
            "decisions": state.get("decisions", []),
        }
    )

    if isinstance(decision, str):
        decision = json.loads(decision)

    # Extract executive decision
    approved = decision.get("approved", False)
    comments = decision.get("comments", "")

    decision_status = "approved" if approved else "rejected"

    entry = {
        "stage": "final_signoff",
        "approved": approved,
        "decision": decision_status,
        "reviewer": "Executive",
        "comments": comments,
        "reasoning": comments or f"Executive {decision_status} the request.",
    }

    return {
        "final_approved": approved,
        "final_comments": comments,
        "current_stage": "processing" if approved else "rejection",
        "decisions": state.get("decisions", []) + [entry],
        "messages": [
            AIMessage(
                content=f"Executive {decision_status} the request. Comments: {comments}"
            )
        ],
    }


def process_request(state: ApprovalState) -> dict:
    """
    Node 7: Process the fully-approved request.

    - Set status to "approved"
    - Set current_stage to "complete"
    - Create a summary message listing all approval stages and comments
    - Call sanitize_output() on the summary before adding to messages
    - Return updated state fields

    Hints:
    - sanitize_output() filters PII from the output text
    """

    summary = (
        f"Request {state.get('request_id')} has been approved.\n"
        f"Request ID: {state.get('request_id')}\n"
        f"Title: {state.get('title')}\n"
        f"Amount: ${state.get('amount', 0):,.2f}\n"
    )

    # Add approval history
    for entry in state.get("decisions", []):
        summary += (
            f"{entry.get('reviewer')}: {entry.get('decision')}  "
            f"{entry.get('comments', '')}\n"
        )

    # Sanitize summary to remove PII
    summary = sanitize_output(summary)

    return {
        "status": "approved",
        "current_stage": "complete",
        "messages": [AIMessage(content=summary)],
    }


def handle_rejection(state: ApprovalState) -> dict:
    """
    Node 8: Handle a rejected request.

    - Set status to "rejected"
    - Set current_stage to "complete"
    - Determine which stage rejected the request from the decisions list
    - Create a rejection summary with the rejection reason
    - Call sanitize_output() on the summary
    - Add an AIMessage with the rejection details
    - Return updated state fields
    """
    summary = (
        f"Request {state.get('request_id')} has been rejected.\n"
        f"Request ID: {state.get('request_id')}\n"
        f"Title: {state.get('title')}\n"
        f"Amount: ${state.get('amount', 0):,.2f}\n"
    )

    # Find which stage rejected the request
    for entry in state.get("decisions", []):
        if not entry.get("approved"):
            summary += (
                f"Rejected by: {entry.get('reviewer')}\n"
                f"Reason: {entry.get('comments', '')}"
            )
            break

    summary = sanitize_output(summary)

    return {
        "status": "rejected",
        "current_stage": "complete",
        "messages": [AIMessage(content=summary)],
    }


# ============================================================
# ROUTING FUNCTIONS (6 total — implement the escalation logic)
# ============================================================


def route_after_submission(state: ApprovalState) -> str:
    """
    Router: After submit_request, go to risk assessment or rejection.


    - Return "assess_risk" if state["is_valid"] is True
    - Return "handle_rejection" otherwise
    """

    # Route to risk assessment if valid, otherwise rejection.

    if state["is_valid"]:
        return "assess_risk"

    return "handle_rejection"


def route_after_risk(state: ApprovalState) -> str:
    """
    Router: After assess_risk, route based on risk level.

    This is the core escalation entry point. Low-risk requests skip
    human review and go directly to budget validation (auto-approve path).
    All other risk levels require manager review first.

    - Return "validate_budget" if risk_level is "low"
    - Return "manager_review" for "medium", "high", or "critical"

    Hints:
    - state["risk_level"] contains the assessed risk level
    - Low risk = auto-approve path (no human review needed if within budget)
    """

    if state["risk_level"] == "low":
        return "validate_budget"

    return "manager_review"


def route_after_manager(state: ApprovalState) -> str:
    """
    Router: After manager_review, route based on approval + risk level.

    The next step depends on BOTH the manager's decision AND the risk level:
    - Rejected → handle_rejection (any risk level)
    - Approved + low risk (over-budget escalation) → process_request
    - Approved + medium risk → validate_budget
    - Approved + high/critical risk → finance_review


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
    if state["manager_approved"] is not True:
        return "handle_rejection"

    risk_level = state["risk_level"]

    if risk_level == "low":
        return "process_request"
    elif risk_level == "medium":
        return "validate_budget"
    else:
        return "finance_review"


def route_after_budget(state: ApprovalState) -> str:
    """
    Router: After validate_budget, route based on budget status + risk level.

    Within-budget requests proceed to processing (auto-approved).
    Over-budget requests escalate to the next human reviewer.


    - Return "process_request" if state["within_budget"] is True
    - If over budget:
      - Return "manager_review" if risk_level is "low" (needs human review)
      - Return "finance_review" if risk_level is "medium" (manager already approved)

    Hints:
    - Low-risk over-budget: first time seeing a human → escalate to manager
    - Medium-risk over-budget: manager already approved → escalate to finance
    - High/critical-risk requests don't go through this router (they skip budget check)
    """
    if state["within_budget"]:
        return "process_request"

    if state["risk_level"] == "low":
        return "manager_review"

    return "finance_review"


def route_after_finance(state: ApprovalState) -> str:
    """
    Router: After finance_review, route based on approval + risk level.

    The next step depends on BOTH finance's decision AND the risk level:
    - Rejected → handle_rejection
    - Approved + critical risk → final_signoff (one more review)
    - Approved + any other risk → process_request (done)


    - Return "handle_rejection" if state["finance_approved"] is not True
    - Return "final_signoff" if risk_level is "critical"
    - Return "process_request" otherwise
    """
    if state["finance_approved"] is not True:
        return "handle_rejection"

    if state["risk_level"] == "critical":
        return "final_signoff"

    return "process_request"


def route_after_final(state: ApprovalState) -> str:
    """
    Router: After final_signoff, go to processing or rejection.


    - Return "process_request" if state["final_approved"] is True
    - Return "handle_rejection" otherwise
    """

    if state["final_approved"] is True:
        return "process_request"

    return "handle_rejection"
