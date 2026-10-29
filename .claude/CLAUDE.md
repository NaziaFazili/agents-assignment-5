# Assignment 5: Financial Approval System with Human-in-the-Loop

## Tech Stack
- **Backend**: Python 3.11+, FastAPI, LangGraph, LangChain
- **Frontend**: Next.js 15, React 19, CopilotKit, Tailwind CSS
- **LLM**: OpenAI GPT-4o-mini (default) or Google Gemini 3.8 Flash
- **Persistence**: SQLite (checkpoints), AsyncSqliteSaver in the server (SqliteSaver for sync scripts)
- **Evaluation**: LangSmith, RAGAS
- **Testing**: pytest

## Project Structure
```
.
├── backend/
│   ├── server.py              # FastAPI + CopilotKit endpoint
│   ├── config.py              # Env loading, LLM factory, budget limits
│   ├── models.py              # Pydantic schemas
│   ├── seed_data.py           # Sample financial requests
│   ├── agent/
│   │   ├── state.py           # ApprovalState TypedDict
│   │   ├── graph.py           # ★ LangGraph StateGraph (STUDENT)
│   │   ├── nodes.py           # ★ 8 nodes + 6 routers (STUDENT)
│   │   └── checkpointer.py   # SQLite checkpointer factory
│   ├── guardrails/
│   │   ├── input_validator.py # ★ Input validation (STUDENT)
│   │   └── output_filter.py  # ★ Output/PII filtering (STUDENT)
│   └── evaluation/
│       ├── dataset.py         # 12 eval test cases
│       ├── evaluators.py      # ★ LangSmith evaluators (STUDENT)
│       ├── run_eval.py        # Evaluation runner
│       ├── three_layer_evaluators.py  # ★ RAGAS 3-layer evaluators (STUDENT)
│       ├── dataset_generator.py       # ★ LLM dataset generation (STUDENT)
│       └── run_three_layer_eval.py    # Three-layer eval runner
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── layout.tsx     # CopilotKit provider
│       │   ├── page.tsx       # Main page with CopilotChat
│       │   └── api/copilotkit/route.ts
│       └── components/
│           ├── ApprovalPanel.tsx # Interrupt UI (useLangGraphInterrupt)
│           ├── RequestForm.tsx
│           ├── WorkflowStatus.tsx
│           └── RequestHistory.tsx
└── tests/                     # Test harnesses (all GIVEN)
```

## Student Tasks (7 files, 125 points + 25 bonus)

### Part 1: LangGraph Workflow (35 pts)
- `backend/agent/nodes.py`: 8 node functions + 6 routing functions
- `backend/agent/graph.py`: StateGraph assembly with conditional edges

### Part 2: Safety Guardrails (20 pts)
- `backend/guardrails/input_validator.py`: validate_request, validate_amount, sanitize_text
- `backend/guardrails/output_filter.py`: sanitize_output, mask_financial_details

### Part 3: CopilotKit Frontend (GIVEN)
- Frontend is fully implemented — study the code to learn the patterns

### Part 4: LangSmith Evaluation (20 pts)
- `backend/evaluation/evaluators.py`: risk accuracy + approval consistency evaluators

### Part 5: Three-Layer Evaluation Framework (50 pts)
- `backend/evaluation/three_layer_evaluators.py`: 10 evaluator factories across 3 layers (34 pts)
  - Layer 1 — Business Metrics (10 pts): approval_path, false_positive, false_negative, human_review_efficiency
  - Layer 2 — Agent Performance (12 pts): RAGAS ToolCallAccuracy, AgentGoalAccuracyWithReference, TopicAdherenceScore (multi_turn_ascore)
  - Layer 3 — Safety & Compliance (12 pts): policy_adherence, hallucination, audit_trail
- `backend/evaluation/dataset_generator.py`: LLM dataset generation + LangSmith upload (16 pts)

## Key Commands

```bash
# Setup
conda create -n hitl-agent python=3.11 -y && conda activate hitl-agent
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# Run
python -m backend.server                    # Backend on :8000
cd frontend && npm run dev                  # Frontend on :3000

# Test
python -m pytest tests/ -v                  # All tests
python -m backend.evaluation.run_eval       # Part 4 evaluation pipeline
python -m backend.evaluation.run_three_layer_eval  # Part 5 three-layer eval
```

## Key Patterns
- **interrupt()**: Pauses graph execution, sends data to frontend
- **Command(resume=value)**: Resumes graph with human decision
- **SqliteSaver / AsyncSqliteSaver**: Checkpoints graph state for interrupt/resume (the server uses AsyncSqliteSaver because AG-UI calls the async graph API)
- **useLangGraphInterrupt**: React hook that fires on graph interrupts
- **resolve()**: Sends decision from frontend back to graph
- **RAGAS metrics** (ragas==0.4.3, from ragas.metrics): ToolCallAccuracy, AgentGoalAccuracyWithReference, TopicAdherenceScore; score with `multi_turn_ascore(MultiTurnSample(...))`. There is no `ragas.metrics.TopicAdherence`, and these metrics have no `single_turn_ascore`. Faithfulness is single-turn (`SingleTurnSample`, `single_turn_ascore`).
- **LangchainLLMWrapper**: Wraps get_llm() for RAGAS metric compatibility
- **convert_to_ragas_messages**: Converts LangGraph traces to RAGAS format
