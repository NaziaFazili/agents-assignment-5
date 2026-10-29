"""
Demo approval graph — a working example with risk-based escalation so
students can see the frontend + HITL interrupt flow before implementing
their own.

Escalation rules (matches the student assignment):
  Low risk      → budget check → auto-approve (or escalate to manager if over budget)
  Medium risk   → manager review → budget check → done (or escalate to finance)
  High risk     → manager → finance → done
  Critical risk → manager → finance → executive → done

Run the backend with:  python -m backend.server
Then open http://localhost:3000 and submit a request.
"""

import json
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from backend.agent.state import ApprovalState
from backend.config import DEPARTMENT_BUDGETS, MEDIUM_RISK_THRESHOLD, HIGH_RISK_THRESHOLD


def _parse_decision(raw_decision) -> tuple[bool, str]:
    """Parse an interrupt decision, handling both str and dict inputs."""
    if isinstance(raw_decision, str):
        raw_decision = json.loads(raw_decision)
    return raw_decision.get("approved", False), raw_decision.get("comments", "")


def _decision_message(role: str, approved: bool, comments: str) -> AIMessage:
    """Build a standard decision AIMessage."""
    status = "approved" if approved else "rejected"
    comment_suffix = f" Comments: {comments}" if comments else ""
    return AIMessage(content=f"{role} {status} the request.{comment_suffix}")


# ============================================================
# NODE FUNCTIONS
# ============================================================

def demo_submit(state: ApprovalState) -> dict:
    """Accept the request and move to risk assessment."""
    title = state.get("title", "Untitled Request")
    amount = state.get("amount", 0)
    dept = state.get("department", "unknown")
    return {
        "is_valid": True,
        # The frontend reuses one thread for every request in a chat session,
        # so clear the previous request's review state from the checkpoint.
        "decisions": [],
        "manager_approved": None, "manager_comments": "",
        "finance_approved": None, "finance_comments": "",
        "final_approved": None, "final_comments": "",
        # None, not 0: high/critical skip the budget check, and the Approval
        # Panel shows "Not checked" only when department_budget is None.
        "department_budget": None, "budget_remaining": None, "within_budget": None,
        "current_stage": "risk_assessment",
        "status": "pending",
        "messages": [
            AIMessage(content=f"Received request: '{title}' for ${amount:,.2f} from {dept} department.")
        ],
    }


def demo_assess(state: ApprovalState) -> dict:
    """Simple rule-based risk assessment (no LLM needed for the demo)."""
    amount = state.get("amount", 0)
    if amount >= 75000:
        level, reasoning = "critical", "Amount exceeds $75,000 — flagged as critical risk."
    elif amount >= HIGH_RISK_THRESHOLD:
        level, reasoning = "high", f"Amount exceeds ${HIGH_RISK_THRESHOLD:,} — flagged as high risk."
    elif amount >= MEDIUM_RISK_THRESHOLD:
        level, reasoning = "medium", f"Amount is between ${MEDIUM_RISK_THRESHOLD:,} and ${HIGH_RISK_THRESHOLD:,}."
    else:
        level, reasoning = "low", f"Amount is under ${MEDIUM_RISK_THRESHOLD:,}."
    return {
        "risk_level": level,
        "risk_reasoning": reasoning,
        "current_stage": "risk_assessed",
        "messages": [AIMessage(content=f"Risk assessment: {level.upper()} — {reasoning}")],
    }


def demo_validate_budget(state: ApprovalState) -> dict:
    """Check the request against department budget."""
    dept = state.get("department", "unknown")
    amount = state.get("amount", 0)
    budget = DEPARTMENT_BUDGETS.get(dept, 0)
    within = amount <= budget
    remaining = budget - amount
    return {
        "department_budget": budget,
        "budget_remaining": remaining,
        "within_budget": within,
        "current_stage": "budget_validated",
        "messages": [
            AIMessage(
                content=(
                    f"Budget check: {dept} budget is ${budget:,.2f}. "
                    f"Request for ${amount:,.2f} is {'within' if within else 'OVER'} budget "
                    f"(remaining: ${remaining:,.2f})."
                )
            )
        ],
    }


def demo_manager_review(state: ApprovalState) -> dict:
    """Manager HITL interrupt."""
    raw = interrupt({
        "type": "manager_review",
        "request_id": state.get("request_id", "DEMO-001"),
        "title": state.get("title", ""),
        "amount": state.get("amount", 0),
        "department": state.get("department", ""),
        "risk_level": state.get("risk_level", "medium"),
        "risk_reasoning": state.get("risk_reasoning", ""),
    })
    approved, comments = _parse_decision(raw)
    return {
        "manager_approved": approved,
        "manager_comments": comments,
        "decisions": state.get("decisions", []) + [{"stage": "manager_review", "approved": approved, "reviewer": "Manager (demo)", "comments": comments}],
        "messages": [_decision_message("Manager", approved, comments)],
    }


def demo_finance_review(state: ApprovalState) -> dict:
    """Finance HITL interrupt."""
    raw = interrupt({
        "type": "finance_review",
        "request_id": state.get("request_id", "DEMO-001"),
        "title": state.get("title", ""),
        "amount": state.get("amount", 0),
        "department": state.get("department", ""),
        "risk_level": state.get("risk_level", "high"),
        "within_budget": state.get("within_budget", True),
        "department_budget": state.get("department_budget", 0),
        "budget_remaining": state.get("budget_remaining", 0),
        "manager_comments": state.get("manager_comments", ""),
    })
    approved, comments = _parse_decision(raw)
    return {
        "finance_approved": approved,
        "finance_comments": comments,
        "decisions": state.get("decisions", []) + [{"stage": "finance_review", "approved": approved, "reviewer": "Finance (demo)", "comments": comments}],
        "messages": [_decision_message("Finance", approved, comments)],
    }


def demo_final_signoff(state: ApprovalState) -> dict:
    """Executive HITL interrupt (critical risk only)."""
    raw = interrupt({
        "type": "final_signoff",
        "request_id": state.get("request_id", "DEMO-001"),
        "title": state.get("title", ""),
        "amount": state.get("amount", 0),
        "department": state.get("department", ""),
        "risk_level": state.get("risk_level", "critical"),
        "manager_approved": state.get("manager_approved", False),
        "finance_approved": state.get("finance_approved", False),
        "within_budget": state.get("within_budget", True),
        "decisions": state.get("decisions", []),
    })
    approved, comments = _parse_decision(raw)
    return {
        "final_approved": approved,
        "final_comments": comments,
        "decisions": state.get("decisions", []) + [{"stage": "final_signoff", "approved": approved, "reviewer": "Executive (demo)", "comments": comments}],
        "messages": [_decision_message("Executive", approved, comments)],
    }


def demo_process(state: ApprovalState) -> dict:
    """Final node — approve and summarise."""
    title = state.get("title", "request")
    risk = state.get("risk_level", "unknown")
    return {
        "status": "approved",
        "current_stage": "complete",
        "messages": [AIMessage(content=f"Request '{title}' (risk: {risk}) has been APPROVED and processed.")],
    }


def demo_reject(state: ApprovalState) -> dict:
    """Final node — rejection summary."""
    title = state.get("title", "request")
    decisions = state.get("decisions", [])
    rejector = "unknown"
    for d in reversed(decisions):
        if not d.get("approved", True):
            rejector = d.get("reviewer", "unknown")
            break
    return {
        "status": "rejected",
        "current_stage": "complete",
        "messages": [AIMessage(content=f"Request '{title}' was REJECTED by {rejector}.")],
    }


# ============================================================
# ROUTING FUNCTIONS (escalation logic)
# ============================================================

def demo_route_after_risk(state: ApprovalState) -> str:
    """Low → budget check (auto-approve path), else → manager."""
    if state.get("risk_level") == "low":
        return "demo_validate_budget"
    return "demo_manager_review"


def demo_route_after_manager(state: ApprovalState) -> str:
    """Manager approved? Route based on risk level."""
    if not state.get("manager_approved"):
        return "demo_reject"
    risk = state.get("risk_level", "medium")
    if risk == "low":
        return "demo_process"
    if risk == "medium":
        return "demo_validate_budget"
    return "demo_finance_review"


def demo_route_after_budget(state: ApprovalState) -> str:
    """Within budget → process; over budget → escalate."""
    if state.get("within_budget"):
        return "demo_process"
    risk = state.get("risk_level", "low")
    if risk == "low":
        return "demo_manager_review"
    return "demo_finance_review"


def demo_route_after_finance(state: ApprovalState) -> str:
    """Finance approved? Critical → executive, else → process."""
    if not state.get("finance_approved"):
        return "demo_reject"
    if state.get("risk_level") == "critical":
        return "demo_final_signoff"
    return "demo_process"


def demo_route_after_final(state: ApprovalState) -> str:
    """Executive approved? → process; rejected → reject."""
    if state.get("final_approved"):
        return "demo_process"
    return "demo_reject"


# ============================================================
# GRAPH ASSEMBLY
# ============================================================

def create_demo_graph(checkpointer=None):
    """Build the demo graph with full escalation routing."""
    graph = StateGraph(ApprovalState)

    # Nodes
    graph.add_node("demo_submit", demo_submit)
    graph.add_node("demo_assess", demo_assess)
    graph.add_node("demo_validate_budget", demo_validate_budget)
    graph.add_node("demo_manager_review", demo_manager_review)
    graph.add_node("demo_finance_review", demo_finance_review)
    graph.add_node("demo_final_signoff", demo_final_signoff)
    graph.add_node("demo_process", demo_process)
    graph.add_node("demo_reject", demo_reject)

    # Entry
    graph.add_edge(START, "demo_submit")
    graph.add_edge("demo_submit", "demo_assess")

    # Conditional edges (escalation routing)
    graph.add_conditional_edges("demo_assess", demo_route_after_risk, {
        "demo_validate_budget": "demo_validate_budget",
        "demo_manager_review": "demo_manager_review",
    })
    graph.add_conditional_edges("demo_manager_review", demo_route_after_manager, {
        "demo_process": "demo_process",
        "demo_validate_budget": "demo_validate_budget",
        "demo_finance_review": "demo_finance_review",
        "demo_reject": "demo_reject",
    })
    graph.add_conditional_edges("demo_validate_budget", demo_route_after_budget, {
        "demo_process": "demo_process",
        "demo_manager_review": "demo_manager_review",
        "demo_finance_review": "demo_finance_review",
    })
    graph.add_conditional_edges("demo_finance_review", demo_route_after_finance, {
        "demo_process": "demo_process",
        "demo_final_signoff": "demo_final_signoff",
        "demo_reject": "demo_reject",
    })
    graph.add_conditional_edges("demo_final_signoff", demo_route_after_final, {
        "demo_process": "demo_process",
        "demo_reject": "demo_reject",
    })

    # Terminal edges
    graph.add_edge("demo_process", END)
    graph.add_edge("demo_reject", END)

    return graph.compile(checkpointer=checkpointer)
