"""
State definition for the Financial Approval workflow.

The ApprovalState extends LangGraph's MessagesState to include
all fields needed for the multi-stage approval process.
"""

from typing import Optional
from langgraph.graph import MessagesState


class ApprovalState(MessagesState):
    """
    State for the financial approval workflow.

    Extends MessagesState to include messages list automatically.
    All fields track the approval request through multiple review stages.
    """
    # --- Request Details ---
    request_id: str
    title: str
    description: str
    amount: float
    department: str
    requester: str
    justification: str
    priority: str

    # --- Risk Assessment ---
    risk_level: str  # "low", "medium", "high", "critical"
    risk_reasoning: str

    # --- Validation ---
    is_valid: bool
    validation_message: str

    # --- Approval Tracking ---
    manager_approved: Optional[bool]
    manager_comments: str
    finance_approved: Optional[bool]
    finance_comments: str
    final_approved: Optional[bool]
    final_comments: str

    # --- Budget ---
    department_budget: float
    budget_remaining: float
    within_budget: bool

    # --- Result ---
    current_stage: str
    status: str  # "pending", "approved", "rejected", "needs_review"
    decisions: list[dict]
