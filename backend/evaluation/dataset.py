"""
Evaluation dataset for the Financial Approval System.

Contains test cases with inputs and expected outputs for
LangSmith evaluation runs. Each case includes the expected
risk level, approval status, and escalation path.

Requests that fail validation (EVAL-007, EVAL-008, EVAL-010) go straight from
submit_request to handle_rejection. assess_risk never runs on that path, so the
graph never sets a risk level and their expected risk_level is None.
"""

EVAL_DATASET = [
    {
        "input": {
            "request_id": "EVAL-001",
            "title": "Office Supplies",
            "description": "Monthly office supply order",
            "amount": 500.00,
            "department": "operations",
            "requester": "Test User",
            "justification": "Regular monthly supplies",
            "priority": "low",
        },
        "expected": {
            "risk_level": "low",
            "status": "approved",
            "approval_path": ["submit_request", "assess_risk", "validate_budget", "process_request"],
            "human_reviews": 0,
        },
    },
    {
        "input": {
            "request_id": "EVAL-002",
            "title": "Server Upgrade",
            "description": "Upgrade production servers for better performance",
            "amount": 25000.00,
            "department": "engineering",
            "requester": "Test User",
            "justification": "Performance degradation affecting customers",
            "priority": "high",
        },
        "expected": {
            "risk_level": "medium",
            "status": "approved",
            "approval_path": ["submit_request", "assess_risk", "manager_review", "validate_budget", "process_request"],
            "human_reviews": 1,
        },
    },
    {
        "input": {
            "request_id": "EVAL-003",
            "title": "Research Equipment",
            "description": "Purchase specialized lab equipment for new research project",
            "amount": 75000.00,
            "department": "research",
            "requester": "Test User",
            "justification": "Required for funded research grant deliverables",
            "priority": "high",
        },
        "expected": {
            "risk_level": "high",
            "status": "approved",
            "approval_path": ["submit_request", "assess_risk", "manager_review", "finance_review", "process_request"],
            "human_reviews": 2,
        },
    },
    {
        "input": {
            "request_id": "EVAL-004",
            "title": "Team Lunch",
            "description": "Quarterly team building lunch event",
            "amount": 800.00,
            "department": "hr",
            "requester": "Test User",
            "justification": "Improve team morale and collaboration",
            "priority": "low",
        },
        "expected": {
            "risk_level": "low",
            "status": "approved",
            "approval_path": ["submit_request", "assess_risk", "validate_budget", "process_request"],
            "human_reviews": 0,
        },
    },
    {
        "input": {
            "request_id": "EVAL-005",
            "title": "Emergency Infrastructure",
            "description": "Critical infrastructure replacement after system failure",
            "amount": 95000.00,
            "department": "engineering",
            "requester": "Test User",
            "justification": "Production system at risk of complete failure",
            "priority": "urgent",
        },
        "expected": {
            "risk_level": "critical",
            "status": "approved",
            "approval_path": ["submit_request", "assess_risk", "manager_review", "finance_review", "final_signoff", "process_request"],
            "human_reviews": 3,
        },
    },
    {
        "input": {
            "request_id": "EVAL-006",
            "title": "Marketing Brochures",
            "description": "Print marketing materials for trade show",
            "amount": 3000.00,
            "department": "marketing",
            "requester": "Test User",
            "justification": "Upcoming industry trade show next month",
            "priority": "normal",
        },
        "expected": {
            "risk_level": "low",
            "status": "approved",
            "approval_path": ["submit_request", "assess_risk", "validate_budget", "process_request"],
            "human_reviews": 0,
        },
    },
    {
        "input": {
            "request_id": "EVAL-007",
            "title": "Unauthorized Purchase",
            "description": "Personal items disguised as business expense",
            "amount": -500.00,
            "department": "operations",
            "requester": "Test User",
            "justification": "Needed for work",
            "priority": "normal",
        },
        "expected": {
            "risk_level": None,  # rejected at submit_request: assess_risk never runs
            "status": "rejected",
            "approval_path": ["submit_request", "handle_rejection"],
            "human_reviews": 0,
        },
    },
    {
        "input": {
            "request_id": "EVAL-008",
            "title": "Massive Purchase",
            "description": "Extremely large purchase exceeding all budgets",
            "amount": 500000.00,
            "department": "engineering",
            "requester": "Test User",
            "justification": "We need everything",
            "priority": "normal",
        },
        "expected": {
            "risk_level": None,  # rejected at submit_request: assess_risk never runs
            "status": "rejected",
            "approval_path": ["submit_request", "handle_rejection"],
            "human_reviews": 0,
        },
    },
    {
        "input": {
            "request_id": "EVAL-009",
            "title": "Software Licenses",
            "description": "Annual renewal of development tool licenses",
            "amount": 15000.00,
            "department": "engineering",
            "requester": "Test User",
            "justification": "Licenses expiring next month, critical for development workflow",
            "priority": "normal",
        },
        "expected": {
            "risk_level": "medium",
            "status": "approved",
            "approval_path": ["submit_request", "assess_risk", "manager_review", "validate_budget", "process_request"],
            "human_reviews": 1,
        },
    },
    {
        "input": {
            "request_id": "EVAL-010",
            "title": "Invalid Department Request",
            "description": "Request from non-existent department",
            "amount": 5000.00,
            "department": "finance",
            "requester": "Test User",
            "justification": "Budget allocation",
            "priority": "normal",
        },
        "expected": {
            "risk_level": None,  # rejected at submit_request: assess_risk never runs
            "status": "rejected",
            "approval_path": ["submit_request", "handle_rejection"],
            "human_reviews": 0,
        },
    },
    {
        "input": {
            "request_id": "EVAL-011",
            "title": "Over-Budget Low-Risk",
            "description": "Low-cost item from a department with very small budget",
            "amount": 8000.00,
            "department": "hr",
            "requester": "Test User",
            "justification": "Training materials for new hire onboarding program",
            "priority": "normal",
        },
        "expected": {
            "risk_level": "low",
            "status": "approved",
            "approval_path": ["submit_request", "assess_risk", "validate_budget", "manager_review", "process_request"],
            "human_reviews": 1,
        },
    },
    {
        "input": {
            "request_id": "EVAL-012",
            "title": "Over-Budget Medium-Risk",
            "description": "Medium expense that exceeds department budget after manager approval",
            "amount": 35000.00,
            "department": "marketing",
            "requester": "Test User",
            "justification": "Major campaign launch requiring significant media buy",
            "priority": "high",
        },
        "expected": {
            "risk_level": "medium",
            "status": "approved",
            "approval_path": ["submit_request", "assess_risk", "manager_review", "validate_budget", "finance_review", "process_request"],
            "human_reviews": 2,
        },
    },
]
