"""
LangGraph StateGraph assembly for the Financial Approval workflow.

Students wire together the 8 nodes and 6 routing functions into
a complete approval pipeline with risk-based escalation and
up to 3 human-in-the-loop interrupts.

Part 1: LangGraph Workflow + Interrupts (35 points)
"""

from langgraph.graph import StateGraph, START, END
from backend.agent.state import ApprovalState
from backend.agent.nodes import (
    submit_request,
    assess_risk,
    manager_review,
    validate_budget,
    finance_review,
    final_signoff,
    process_request,
    handle_rejection,
    route_after_submission,
    route_after_risk,
    route_after_manager,
    route_after_budget,
    route_after_finance,
    route_after_final,
)


def create_approval_graph(checkpointer=None):
    """
    Build and return the compiled Financial Approval StateGraph.

    The graph implements risk-based escalation:
    - Low risk:      auto-approve → budget check → done (0 human reviews)
    - Medium risk:   manager review → budget check → done (1 human review)
    - High risk:     manager → finance review → done (2 human reviews)
    - Critical risk: manager → finance → executive sign-off (3 human reviews)
    - Over-budget:   escalates to the next human reviewer

    TODO (10 points):
    - Create a StateGraph with ApprovalState
    - Add all 8 nodes:
        "submit_request", "assess_risk", "manager_review",
        "validate_budget", "finance_review", "final_signoff",
        "process_request", "handle_rejection"
    - Set entry point to "submit_request"
    - Add conditional edges with 6 routing functions:
        submit_request  → route_after_submission → assess_risk | handle_rejection
        assess_risk     → route_after_risk       → validate_budget | manager_review
        manager_review  → route_after_manager    → process_request | validate_budget | finance_review | handle_rejection
        validate_budget → route_after_budget     → process_request | manager_review | finance_review
        finance_review  → route_after_finance    → process_request | final_signoff | handle_rejection
        final_signoff   → route_after_final      → process_request | handle_rejection
    - Add terminal edges:
        process_request  → END
        handle_rejection → END
    - Compile and return the graph

    Args:
        checkpointer: checkpointer for persisting graph state across
                      interrupt/resume cycles (server.py passes an
                      AsyncSqliteSaver; sync scripts can pass SqliteSaver)

    Hints:
    - Use graph.add_node("name", function) for each node
    - Use graph.add_edge(START, "submit_request") for the entry edge
    - Use graph.add_conditional_edges("source", router_fn, {"value": "target", ...})
    - Use graph.add_edge("source", "target") for direct edges
    - Return graph.compile(checkpointer=checkpointer)

    Returns:
        Compiled StateGraph ready for execution
    """
    raise NotImplementedError("TODO: Implement create_approval_graph (10 points)")
