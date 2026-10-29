"""
Sample financial requests for testing and demonstration.
Covers a range of amounts, departments, and risk levels.
"""

from backend.models import FinancialRequest

SAMPLE_REQUESTS = [
    FinancialRequest(
        request_id="REQ-001",
        title="Cloud Infrastructure Upgrade",
        description="Upgrade AWS infrastructure to support increased traffic and improve reliability.",
        amount=45000.00,
        department="engineering",
        requester="Alice Chen",
        justification="Current infrastructure is at 85% capacity. Upgrade needed to handle projected 40% traffic increase in Q3.",
        priority="high",
    ),
    FinancialRequest(
        request_id="REQ-002",
        title="Q3 Marketing Campaign",
        description="Digital marketing campaign across social media and search platforms for product launch.",
        amount=15000.00,
        department="marketing",
        requester="Bob Martinez",
        justification="Product launch scheduled for Q3. Campaign expected to generate 2x ROI based on Q1 results.",
        priority="normal",
    ),
    FinancialRequest(
        request_id="REQ-003",
        title="Office Supply Restock",
        description="Quarterly office supplies order including paper, pens, and printer cartridges.",
        amount=2500.00,
        department="operations",
        requester="Carol White",
        justification="Regular quarterly restock. Current supplies projected to run out in 2 weeks.",
        priority="low",
    ),
    FinancialRequest(
        request_id="REQ-004",
        title="AI Research Equipment",
        description="Purchase of GPU servers for machine learning research and model training.",
        amount=85000.00,
        department="research",
        requester="David Kim",
        justification="Current GPU capacity insufficient for training large language models. New hardware will reduce training time by 60%.",
        priority="high",
    ),
    FinancialRequest(
        request_id="REQ-005",
        title="Employee Training Program",
        description="Annual professional development and certification program for engineering team.",
        amount=12000.00,
        department="hr",
        requester="Eva Johnson",
        justification="Industry certifications improve team capabilities and retention. 90% of participants reported increased job satisfaction last year.",
        priority="normal",
    ),
    FinancialRequest(
        request_id="REQ-006",
        title="Emergency Server Replacement",
        description="Replace failed production database server with redundant backup system.",
        amount=95000.00,
        department="engineering",
        requester="Frank Liu",
        justification="Primary database server showing hardware failures. Risk of complete data loss without immediate replacement.",
        priority="urgent",
    ),
]
