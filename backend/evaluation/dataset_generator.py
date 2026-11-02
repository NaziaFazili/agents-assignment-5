"""
LLM-based evaluation dataset generator for the Financial Approval System.

Students implement functions to:
1. Generate diverse test cases using an LLM
2. Generate edge/adversarial cases
3. Upload datasets to LangSmith
4. Validate generated datasets

Part 5: Dataset Generation (16 points)
"""

import json

import langsmith

from backend import config

# ---------------------------------------------------------------------------
# Constants (GIVEN — do not modify)
# ---------------------------------------------------------------------------

VALID_DEPARTMENTS = ["engineering", "marketing", "operations", "research", "hr"]

BUDGET_CEILING = 100_000

DEPARTMENT_BUDGETS = {
    "engineering": 50000,
    "marketing": 30000,
    "operations": 40000,
    "research": 60000,
    "hr": 5000,
}

DATASET_SCHEMA = {
    "input": {
        "request_id": "str — unique identifier (e.g., 'GEN-001')",
        "title": "str — short description of the purchase",
        "description": "str — detailed description",
        "amount": "float — dollar amount (can be negative for edge cases)",
        "department": "str — one of VALID_DEPARTMENTS",
        "requester": "str — person making the request",
        "justification": "str — business justification",
        "priority": "str — one of: low, normal, high, urgent",
    },
    "expected": {
        "risk_level": "str or None: one of low, medium, high, critical; None (JSON null) "
        "when the request is rejected at submit_request, because assess_risk never runs",
        "status": "str — one of: approved, rejected",
        "approval_path": "list[str] — ordered list of workflow stages",
        "human_reviews": "int — number of human review interrupts expected",
    },
}

OUTPUT_FORMAT = """
Output format (validate_generated_dataset rejects a case that does not follow it):
Each test case is a JSON object with exactly two keys, "input" and "expected".
"input" has all 8 of these fields:
  "request_id": string, unique (e.g. "GEN-001")
  "title": string, short name of the purchase
  "description": string, details of the purchase
  "amount": number, not a string (dollars)
  "department": one of {departments}
  "requester": string, name of the person making the request
  "justification": string, business reason for the purchase
  "priority": one of "low", "normal", "high", "urgent"
"expected" has all 4 of these fields:
  "risk_level": one of "low", "medium", "high", "critical", or null when the request is
    rejected at submit_request (its approval_path has no "assess_risk")
  "status": "approved" or "rejected" (lowercase)
  "approval_path": list of stage names in order, taken from: "submit_request",
    "assess_risk", "validate_budget", "manager_review", "finance_review",
    "final_signoff", "process_request", "handle_rejection"
  "human_reviews": integer >= 0, the number of "manager_review", "finance_review" and
    "final_signoff" stages in approval_path
Use these key names exactly ("approval_path", not "path"; "human_reviews", not
"review_count" or "required_reviews"). risk_level, status and priority are lowercase.
Expected values assume every human reviewer approves, so "rejected" is only for
requests rejected at submit_request.

Example of one test case:
{{"input": {{"request_id": "GEN-001", "title": "Team Laptops",
  "description": "Three laptops for new hires", "amount": 4500.0,
  "department": "engineering", "requester": "Dana Lee",
  "justification": "New hires start next month", "priority": "normal"}},
 "expected": {{"risk_level": "low", "status": "approved",
  "approval_path": ["submit_request", "assess_risk", "validate_budget", "process_request"],
  "human_reviews": 0}}}}

Return ONLY a JSON array of test case objects. No markdown, no explanation.
"""

GENERATION_PROMPT = (
    """You are a test case generator for a Financial Approval System.

Generate {num_cases} diverse test cases for evaluating the system. Each test case
should be a JSON object with "input" and "expected" fields.

Business Rules:
- Amounts <= $10,000: low risk, auto-approved (0 human reviews)
  Path: submit_request → assess_risk → validate_budget → process_request
- Amounts $10,001-$50,000: medium risk, needs manager review (1 human review)
  Path: submit_request → assess_risk → manager_review → validate_budget → process_request
- Amounts $50,001-$100,000: high risk, needs manager + finance review (2 human reviews)
  Path: submit_request → assess_risk → manager_review → finance_review → process_request
- Amounts > $100,000: rejected (exceeds budget ceiling)
  Path: submit_request → handle_rejection
- Zero or negative amounts: rejected (invalid)
  Path: submit_request → handle_rejection
- Requests rejected at submit_request never reach assess_risk: their expected
  risk_level is null
- Priority "urgent" + amount > $50,000: critical risk, needs 3 reviews
  Path: submit_request → assess_risk → manager_review → finance_review → final_signoff → process_request
- Department budgets: engineering $50,000, marketing $30,000, operations $40,000,
  research $60,000, hr $5,000. validate_budget escalates when the amount is over budget:
  - Low risk over budget: manager review (1 human review)
    Path: submit_request → assess_risk → validate_budget → manager_review → process_request
  - Medium risk over budget: finance review after the budget check (2 human reviews)
    Path: submit_request → assess_risk → manager_review → validate_budget → finance_review → process_request

Valid departments: {departments}
Valid priorities: low, normal, high, urgent

Generate realistic financial requests covering different departments, amounts,
and risk levels. Include a mix of approved and rejected cases.
"""
    + OUTPUT_FORMAT
)

EDGE_CASE_PROMPT = (
    """You are a test case generator for a Financial Approval System.
Generate {num_cases} EDGE CASES and ADVERSARIAL scenarios.

Focus on boundary conditions and tricky scenarios:
1. Amounts exactly at thresholds ($10,000, $50,000, $100,000)
2. Negative amounts or zero amounts
3. Very large amounts (> $1,000,000)
4. Unusual descriptions that might confuse the system
5. Requests that test policy boundaries

Business Rules:
- Amounts <= $10,000: low risk, auto-approved (0 human reviews)
  Path: submit_request → assess_risk → validate_budget → process_request
- Amounts $10,001-$50,000: medium risk, manager review (1 human review)
  Path: submit_request → assess_risk → manager_review → validate_budget → process_request
- Amounts $50,001-$100,000: high risk, manager + finance review (2 human reviews)
  Path: submit_request → assess_risk → manager_review → finance_review → process_request
- Priority "urgent" + amount > $50,000: critical risk, 3 reviews (no budget check)
  Path: submit_request → assess_risk → manager_review → finance_review → final_signoff → process_request
- Rejected at submit_request: amounts > $100,000, zero or negative amounts, and text
  containing SQL or script injection (for example "<script>" or "' or '1'='1")
  Path: submit_request → handle_rejection. These never reach assess_risk: their
  expected risk_level is null and human_reviews is 0
- Over the department budget (engineering $50,000, marketing $30,000, operations $40,000,
  research $60,000, hr $5,000), only for low and medium risk:
  - Low risk: submit_request → assess_risk → validate_budget → manager_review → process_request (1 review)
  - Medium risk: submit_request → assess_risk → manager_review → validate_budget → finance_review → process_request (2 reviews)

Valid departments: {departments}
Use only these departments: an invalid department fails validate_generated_dataset.
"""
    + OUTPUT_FORMAT
)


# ═══════════════════════════════════════════════════════════════════════════
# Dataset Generation Functions (16 points)
# ═══════════════════════════════════════════════════════════════════════════


def generate_eval_dataset(num_cases=10, llm=None):
    """
    Generate diverse evaluation test cases using an LLM.


    - If llm is None, create one using: from backend.config import get_llm
    - Format GENERATION_PROMPT with num_cases and VALID_DEPARTMENTS
    - Invoke the LLM with the formatted prompt: response = llm.invoke(prompt)
    - Parse the JSON response into a list of dicts: json.loads(response.text)
      (.text is a property, no parentheses; response.content is a list of content
      blocks with Gemini, and json.loads() on it raises TypeError. If the model wraps
      the array in a ```json fence anyway, strip the fence before json.loads)
    - Each dict must match DATASET_SCHEMA structure
    - Return the list of generated test cases

    Args:
        num_cases: Number of test cases to generate (default 10)
        llm: Optional LangChain LLM instance (if None, use get_llm())

    Returns:
        list[dict]: Generated test cases matching DATASET_SCHEMA

    Example:
        dataset = generate_eval_dataset(num_cases=5)
        # Returns: [{"input": {...}, "expected": {...}}, ...]
    """
    # Create LLM if one wasn't provided
    if llm is None:
        from backend.config import get_llm

        llm = get_llm()

    # Prepare the prompt
    prompt = GENERATION_PROMPT.format(
        num_cases=num_cases, valid_departments=VALID_DEPARTMENTS
    )

    # Ask LLM to generate test cases
    response = llm.invoke(prompt)

    # Get JSON text
    text = response.text.strip()

    # Remove JSON code fences
    text = text.removeprefix("```json").removeprefix("```")
    text = text.removesuffix("```").strip()

    # Convert JSON text into Python objects
    dataset = json.loads(text)

    is_valid, errors = validate_generated_dataset(dataset)

    if not is_valid:
        raise ValueError(f"Invalid generated dataset: {errors}")

    return dataset


def generate_edge_cases(num_cases=5, llm=None):
    """
    Generate boundary and adversarial test cases using an LLM.


    - If llm is None, create one using: from backend.config import get_llm
    - Format EDGE_CASE_PROMPT with num_cases and VALID_DEPARTMENTS
    - Invoke the LLM with the formatted prompt: response = llm.invoke(prompt)
    - Parse the JSON response into a list of dicts: json.loads(response.text)
      (.text is a property, no parentheses; response.content is a list of content
      blocks with Gemini, and json.loads() on it raises TypeError. If the model wraps
      the array in a ```json fence anyway, strip the fence before json.loads)
    - Focus on boundary conditions (exact thresholds, negatives, etc.)
    - Return the list of generated edge cases

    Args:
        num_cases: Number of edge cases to generate (default 5)
        llm: Optional LangChain LLM instance (if None, use get_llm())

    Returns:
        list[dict]: Generated edge cases matching DATASET_SCHEMA
    """
    if llm is None:
        from backend.config import get_llm

        llm = get_llm()

    # Prepare the edge-case prompt
    prompt = EDGE_CASE_PROMPT.format(
        num_cases=num_cases, valid_departments=VALID_DEPARTMENTS
    )

    # Generate edge cases
    response = llm.invoke(prompt)

    # Remove JSON code fences if present
    text = response.text.strip()
    text = text.removeprefix("```json").removeprefix("```")
    text = text.removesuffix("```").strip()

    # Convert JSON into a Python list
    dataset = json.loads(text)

    return dataset


def upload_to_langsmith(dataset, dataset_name="financial-approval-eval"):
    """
    Upload a dataset to LangSmith for evaluation runs.

    - Import langsmith and create a Client: client = langsmith.Client()
      (it reads LANGSMITH_API_KEY from the environment. Importing backend.config
      loads .env; if nothing has loaded it, the client sends no key and
      LangSmith answers 401 "Invalid token")
    - Create a new dataset: ls_dataset = client.create_dataset(dataset_name=dataset_name)
      (use a new name; the `dataset` argument is your list of test cases)
    - For each test case in the dataset, create an example:
        client.create_example(
            inputs=case["input"],
            outputs=case["expected"],
            dataset_id=ls_dataset.id,
        )
    - Return the dataset ID as a string

    Args:
        dataset: list[dict] — test cases with "input" and "expected" keys
        dataset_name: str — name for the LangSmith dataset

    Returns:
        str: The LangSmith dataset ID

    Raises:
        ValueError: If dataset is empty
    """
    if not dataset:
        raise ValueError("Dataset cannot be empty")

    client = langsmith.Client()

    # Create a dataset in LangSmith
    ls_dataset = client.create_dataset(dataset_name=dataset_name)

    # Upload each test case
    for case in dataset:
        client.create_example(
            inputs=case["input"], outputs=case["expected"], dataset_id=ls_dataset.id
        )

    return str(ls_dataset.id)


def validate_generated_dataset(dataset):
    """
    Validate that a generated dataset conforms to the expected schema.


    - Check the following and collect error messages for failures:
      1. dataset is a non-empty list
      2. Each entry has "input" and "expected" top-level keys
      3. Each input has required fields: request_id, title, description,
         amount, department, requester, justification, priority
      4. Each expected has required fields: risk_level, status,
         approval_path, human_reviews
      5. amount is a number (int or float)
      6. department is in VALID_DEPARTMENTS
      7. risk_level is one of: low, medium, high, critical, or None when
         approval_path skips "assess_risk" (rejected at submit_request)
      8. status is one of: approved, rejected
      9. approval_path is a list
      10. human_reviews is an int >= 0
    - Return a tuple: (is_valid: bool, errors: list[str])
      - is_valid is True if no errors found
      - errors is a list of descriptive error strings

    Args:
        dataset: list[dict] — the dataset to validate

    Returns:
        tuple[bool, list[str]]: (is_valid, error_messages)

    Example:
        valid, errors = validate_generated_dataset([{"input": {}, "expected": {}}])
        # valid = False, errors = ["Case 1: input missing 'request_id'", ...]
    """
    errors = []

    # 1. Dataset must be a non-empty list
    if not isinstance(dataset, list) or len(dataset) == 0:
        return False, ["Dataset must be a non-empty list"]

    input_fields = [
        "request_id",
        "title",
        "description",
        "amount",
        "department",
        "requester",
        "justification",
        "priority",
    ]

    expected_fields = ["risk_level", "status", "approval_path", "human_reviews"]

    valid_risks = ["low", "medium", "high", "critical"]

    for index, case in enumerate(dataset, start=1):
        # 2. Check top-level keys
        if not isinstance(case, dict):
            errors.append(f"Case {index}: Must be a dictionary")
            continue

        if "input" not in case or "expected" not in case:
            errors.append(f"Case {index}: Missing input or expected")
            continue

        inputs = case["input"]
        expected = case["expected"]

        if not isinstance(inputs, dict) or not isinstance(expected, dict):
            errors.append(f"Case {index}: input and expected must be dictionaries")
            continue

        # 3. Check required input fields
        for field in input_fields:
            if field not in inputs:
                errors.append(f"Case {index}: input missing '{field}'")

        # 4. Check required expected fields
        for field in expected_fields:
            if field not in expected:
                errors.append(f"Case {index}: expected missing '{field}'")

        # 5. Check amount
        if not isinstance(inputs.get("amount"), (int, float)):
            errors.append(f"Case {index}: amount must be a number")

        # 6. Check department
        if inputs.get("department") not in VALID_DEPARTMENTS:
            errors.append(f"Case {index}: invalid department")

        # 7. Check risk level
        risk = expected.get("risk_level")
        path = expected.get("approval_path", [])

        if risk not in valid_risks:
            if not (
                risk is None and isinstance(path, list) and "assess_risk" not in path
            ):
                errors.append(f"Case {index}: invalid risk level")

        # 8. Check status
        if expected.get("status") not in ["approved", "rejected"]:
            errors.append(f"Case {index}: invalid status")

        # 9. Check approval path
        if not isinstance(path, list):
            errors.append(f"Case {index}: approval_path must be a list")

        # 10. Check human reviews
        reviews = expected.get("human_reviews")

        if not isinstance(reviews, int) or isinstance(reviews, bool) or reviews < 0:
            errors.append(f"Case {index}: human_reviews must be a non-negative integer")

    return len(errors) == 0, errors
