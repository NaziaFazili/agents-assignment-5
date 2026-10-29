"""
Configuration for the Financial Approval System.
Loads environment variables and provides LLM factory.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM Configuration ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # "openai" or "google"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-3.8-flash")

# --- Budget Limits ---
BUDGET_CEILING = float(os.getenv("BUDGET_CEILING", "100000"))  # $100,000 max
DEPARTMENT_BUDGETS = {
    "engineering": 50000,
    "marketing": 30000,
    "operations": 40000,
    "research": 60000,
    "hr": 5000,  # below the $10k low-risk ceiling, so "low risk + over budget" (EVAL-011) is reachable
}
VALID_DEPARTMENTS = list(DEPARTMENT_BUDGETS.keys())

# --- Risk Thresholds ---
HIGH_RISK_THRESHOLD = 50000
MEDIUM_RISK_THRESHOLD = 10000

# --- LangSmith ---
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "financial-approval-system")

# --- Checkpointer ---
CHECKPOINT_DB = os.getenv("CHECKPOINT_DB", "checkpoints.db")


def get_llm(temperature: float = 0.0):
    """Factory function to create the appropriate LLM based on LLM_PROVIDER."""
    if LLM_PROVIDER == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=GOOGLE_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=temperature,
        )

    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=OPENAI_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=temperature,
    )
