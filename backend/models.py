"""
Pydantic models for the Financial Approval System.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class Department(str, Enum):
    ENGINEERING = "engineering"
    MARKETING = "marketing"
    OPERATIONS = "operations"
    RESEARCH = "research"
    HR = "hr"


class FinancialRequest(BaseModel):
    """A financial approval request."""
    request_id: str = Field(description="Unique request identifier")
    title: str = Field(description="Brief title of the request")
    description: str = Field(description="Detailed description of the request")
    amount: float = Field(description="Requested amount in USD")
    department: str = Field(description="Requesting department")
    requester: str = Field(description="Name of the person making the request")
    justification: str = Field(description="Business justification for the request")
    priority: str = Field(default="normal", description="Priority level: low, normal, high, urgent")


class ApprovalDecision(BaseModel):
    """A decision made at an approval stage."""
    stage: str = Field(description="Approval stage name")
    approved: bool = Field(description="Whether the request was approved at this stage")
    reviewer: str = Field(description="Name/role of the reviewer")
    comments: str = Field(default="", description="Review comments")
    timestamp: Optional[str] = Field(default=None, description="ISO timestamp of decision")


class ApprovalResult(BaseModel):
    """Final result of the approval workflow."""
    request_id: str
    status: ApprovalStatus
    risk_level: RiskLevel
    decisions: list[ApprovalDecision] = Field(default_factory=list)
    total_approvals: int = 0
    total_rejections: int = 0
    final_comments: str = ""
