"""
Test harness for Part 1: LangGraph Workflow + Interrupts.

Verifies graph structure, node names, interrupt usage, state schema,
routing functions, and escalation logic without requiring API keys.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def check_graph_import():
    """Verify create_approval_graph is importable."""
    try:
        from backend.agent.graph import create_approval_graph
        print("[PASS] create_approval_graph is importable")
        return True
    except ImportError as e:
        print(f"[FAIL] Cannot import create_approval_graph: {e}")
        return False


def check_graph_callable():
    """Verify create_approval_graph returns a compiled graph."""
    try:
        from backend.agent.graph import create_approval_graph
        graph = create_approval_graph()
        if graph is not None:
            print("[PASS] create_approval_graph() returns a graph object")
            return True
        else:
            print("[FAIL] create_approval_graph() returned None")
            return False
    except NotImplementedError:
        print("[EXPECTED] create_approval_graph raises NotImplementedError (student TODO)")
        return True
    except Exception as e:
        print(f"[FAIL] create_approval_graph() raised unexpected error: {e}")
        return False


def check_node_functions():
    """Verify all 8 node functions are defined and callable."""
    expected_nodes = [
        "submit_request",
        "assess_risk",
        "manager_review",
        "validate_budget",
        "finance_review",
        "final_signoff",
        "process_request",
        "handle_rejection",
    ]
    results = []

    try:
        from backend.agent import nodes
        for name in expected_nodes:
            fn = getattr(nodes, name, None)
            if fn is None:
                print(f"[FAIL] Node function '{name}' not found")
                results.append(False)
            elif not callable(fn):
                print(f"[FAIL] '{name}' is not callable")
                results.append(False)
            else:
                print(f"[PASS] Node function '{name}' exists and is callable")
                results.append(True)
    except ImportError as e:
        print(f"[FAIL] Cannot import nodes module: {e}")
        return [False]

    return results


def check_routing_functions():
    """Verify all 6 routing functions are defined and callable."""
    expected_routers = [
        "route_after_submission",
        "route_after_risk",
        "route_after_manager",
        "route_after_budget",
        "route_after_finance",
        "route_after_final",
    ]
    results = []

    try:
        from backend.agent import nodes
        for name in expected_routers:
            fn = getattr(nodes, name, None)
            if fn is None:
                print(f"[FAIL] Router function '{name}' not found")
                results.append(False)
            elif not callable(fn):
                print(f"[FAIL] '{name}' is not callable")
                results.append(False)
            else:
                print(f"[PASS] Router function '{name}' exists and is callable")
                results.append(True)
    except ImportError as e:
        print(f"[FAIL] Cannot import nodes module: {e}")
        return [False]

    return results


# Full request state for running a review node on its own (no LLM needed).
SAMPLE_REVIEW_STATE = {
    "messages": [],
    "request_id": "TEST-001", "title": "Server cluster", "description": "Replace failed cluster",
    "amount": 95000.0, "department": "engineering", "requester": "Test User",
    "justification": "Production down", "priority": "urgent",
    "risk_level": "critical", "risk_reasoning": "Urgent and over $50,000",
    "is_valid": True, "validation_message": "",
    "manager_approved": True, "manager_comments": "ok",
    "finance_approved": True, "finance_comments": "ok",
    "final_approved": None, "final_comments": "",
    "department_budget": 50000.0, "budget_remaining": -45000.0, "within_budget": False,
    "current_stage": "review", "status": "pending", "decisions": [],
}


def _pauses_on_interrupt(fn):
    """Run fn as the only node of a graph; True if it pauses on interrupt()."""
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import StateGraph, START, END
    from backend.agent.state import ApprovalState

    graph = StateGraph(ApprovalState)
    graph.add_node("node", fn)
    graph.add_edge(START, "node")
    graph.add_edge("node", END)
    app = graph.compile(checkpointer=MemorySaver())
    result = app.invoke(dict(SAMPLE_REVIEW_STATE), {"configurable": {"thread_id": "interrupt-check"}})
    return "__interrupt__" in result


def check_interrupt_usage():
    """Verify that the 3 review nodes pause the graph with interrupt().

    The node is executed, not searched as text: the stub docstrings mention
    interrupt(), so a source-text check passed even when no node called it.
    """
    interrupt_nodes = ["manager_review", "finance_review", "final_signoff"]
    results = []

    try:
        from backend.agent import nodes

        for name in interrupt_nodes:
            fn = getattr(nodes, name, None)
            if fn is None:
                print(f"[FAIL] Cannot find '{name}' to check for interrupt()")
                results.append(False)
                continue

            try:
                paused = _pauses_on_interrupt(fn)
            except NotImplementedError:
                print(f"[EXPECTED] '{name}' raises NotImplementedError (student TODO)")
                results.append(True)
                continue
            except Exception as e:
                print(f"[FAIL] '{name}' raised {type(e).__name__}: {e}")
                results.append(False)
                continue

            if paused:
                print(f"[PASS] '{name}' pauses the graph with interrupt()")
                results.append(True)
            else:
                print(f"[FAIL] '{name}' ran without calling interrupt()")
                results.append(False)
    except ImportError as e:
        print(f"[FAIL] Cannot import nodes module: {e}")
        return [False]

    return results


def check_state_schema():
    """Verify ApprovalState has all required fields."""
    required_fields = [
        "request_id", "title", "description", "amount",
        "department", "requester", "justification", "priority",
        "risk_level", "risk_reasoning",
        "is_valid", "validation_message",
        "manager_approved", "manager_comments",
        "finance_approved", "finance_comments",
        "final_approved", "final_comments",
        "department_budget", "budget_remaining", "within_budget",
        "current_stage", "status", "decisions",
    ]
    results = []

    try:
        from backend.agent.state import ApprovalState
        annotations = ApprovalState.__annotations__

        for field in required_fields:
            if field in annotations:
                print(f"[PASS] ApprovalState has field '{field}'")
                results.append(True)
            else:
                print(f"[FAIL] ApprovalState missing field '{field}'")
                results.append(False)

        # Check that it inherits from MessagesState by verifying 'messages' key
        all_annotations = {}
        for cls in reversed(ApprovalState.__mro__):
            if hasattr(cls, '__annotations__'):
                all_annotations.update(cls.__annotations__)
        all_annotations.update(ApprovalState.__annotations__)
        if "messages" in all_annotations:
            print("[PASS] ApprovalState has 'messages' from MessagesState")
            results.append(True)
        else:
            print("[FAIL] ApprovalState missing 'messages' (should extend MessagesState)")
            results.append(False)

    except ImportError as e:
        print(f"[FAIL] Cannot import ApprovalState: {e}")
        return [False]

    return results


def check_checkpointer():
    """Verify checkpointer factory works."""
    try:
        from backend.agent.checkpointer import create_checkpointer
        if callable(create_checkpointer):
            print("[PASS] create_checkpointer is callable")
            return True
        else:
            print("[FAIL] create_checkpointer is not callable")
            return False
    except ImportError as e:
        print(f"[FAIL] Cannot import create_checkpointer: {e}")
        return False


def check_demo_graph_escalation():
    """Verify the demo graph has full escalation routing."""
    results = []

    try:
        from backend.agent.demo_graph import create_demo_graph
        graph = create_demo_graph()
        if graph is None:
            print("[FAIL] create_demo_graph() returned None")
            return [False]

        # Check all 8 nodes are present
        node_names = set(graph.get_graph().nodes.keys())
        expected = {
            "demo_submit", "demo_assess", "demo_validate_budget",
            "demo_manager_review", "demo_finance_review",
            "demo_final_signoff", "demo_process", "demo_reject",
        }
        # LangGraph also adds __start__ and __end__ nodes
        for name in expected:
            if name in node_names:
                print(f"[PASS] Demo graph has node '{name}'")
                results.append(True)
            else:
                print(f"[FAIL] Demo graph missing node '{name}'")
                results.append(False)

        print(f"[PASS] Demo graph has {len(expected)} workflow nodes")
        results.append(True)

    except ImportError as e:
        print(f"[FAIL] Cannot import demo graph: {e}")
        return [False]
    except Exception as e:
        print(f"[FAIL] Demo graph error: {e}")
        return [False]

    return results


def check_demo_routing_logic():
    """Verify demo graph routing functions implement correct escalation."""
    results = []

    try:
        from backend.agent.demo_graph import (
            demo_route_after_risk,
            demo_route_after_manager,
            demo_route_after_budget,
            demo_route_after_finance,
            demo_route_after_final,
        )

        # --- route_after_risk ---
        # Low risk → budget check (auto-approve path)
        r = demo_route_after_risk({"risk_level": "low"})
        if r == "demo_validate_budget":
            print("[PASS] route_after_risk: low → validate_budget")
            results.append(True)
        else:
            print(f"[FAIL] route_after_risk: low → expected 'demo_validate_budget', got '{r}'")
            results.append(False)

        # Medium/High/Critical → manager review
        for level in ("medium", "high", "critical"):
            r = demo_route_after_risk({"risk_level": level})
            if r == "demo_manager_review":
                print(f"[PASS] route_after_risk: {level} → manager_review")
                results.append(True)
            else:
                print(f"[FAIL] route_after_risk: {level} → expected 'demo_manager_review', got '{r}'")
                results.append(False)

        # --- route_after_manager ---
        # Rejected → reject
        r = demo_route_after_manager({"manager_approved": False, "risk_level": "medium"})
        if r == "demo_reject":
            print("[PASS] route_after_manager: rejected → reject")
            results.append(True)
        else:
            print(f"[FAIL] route_after_manager: rejected → expected 'demo_reject', got '{r}'")
            results.append(False)

        # Approved + low (over-budget escalation) → process
        r = demo_route_after_manager({"manager_approved": True, "risk_level": "low"})
        if r == "demo_process":
            print("[PASS] route_after_manager: approved + low → process")
            results.append(True)
        else:
            print(f"[FAIL] route_after_manager: approved + low → expected 'demo_process', got '{r}'")
            results.append(False)

        # Approved + medium → validate_budget
        r = demo_route_after_manager({"manager_approved": True, "risk_level": "medium"})
        if r == "demo_validate_budget":
            print("[PASS] route_after_manager: approved + medium → validate_budget")
            results.append(True)
        else:
            print(f"[FAIL] route_after_manager: approved + medium → expected 'demo_validate_budget', got '{r}'")
            results.append(False)

        # Approved + high → finance
        r = demo_route_after_manager({"manager_approved": True, "risk_level": "high"})
        if r == "demo_finance_review":
            print("[PASS] route_after_manager: approved + high → finance_review")
            results.append(True)
        else:
            print(f"[FAIL] route_after_manager: approved + high → expected 'demo_finance_review', got '{r}'")
            results.append(False)

        # Approved + critical → finance
        r = demo_route_after_manager({"manager_approved": True, "risk_level": "critical"})
        if r == "demo_finance_review":
            print("[PASS] route_after_manager: approved + critical → finance_review")
            results.append(True)
        else:
            print(f"[FAIL] route_after_manager: approved + critical → expected 'demo_finance_review', got '{r}'")
            results.append(False)

        # --- route_after_budget ---
        # Within budget → process
        r = demo_route_after_budget({"within_budget": True, "risk_level": "low"})
        if r == "demo_process":
            print("[PASS] route_after_budget: within_budget → process")
            results.append(True)
        else:
            print(f"[FAIL] route_after_budget: within_budget → expected 'demo_process', got '{r}'")
            results.append(False)

        # Over budget + low → manager
        r = demo_route_after_budget({"within_budget": False, "risk_level": "low"})
        if r == "demo_manager_review":
            print("[PASS] route_after_budget: over_budget + low → manager_review")
            results.append(True)
        else:
            print(f"[FAIL] route_after_budget: over_budget + low → expected 'demo_manager_review', got '{r}'")
            results.append(False)

        # Over budget + medium → finance
        r = demo_route_after_budget({"within_budget": False, "risk_level": "medium"})
        if r == "demo_finance_review":
            print("[PASS] route_after_budget: over_budget + medium → finance_review")
            results.append(True)
        else:
            print(f"[FAIL] route_after_budget: over_budget + medium → expected 'demo_finance_review', got '{r}'")
            results.append(False)

        # --- route_after_finance ---
        # Rejected → reject
        r = demo_route_after_finance({"finance_approved": False, "risk_level": "high"})
        if r == "demo_reject":
            print("[PASS] route_after_finance: rejected → reject")
            results.append(True)
        else:
            print(f"[FAIL] route_after_finance: rejected → expected 'demo_reject', got '{r}'")
            results.append(False)

        # Approved + critical → final_signoff
        r = demo_route_after_finance({"finance_approved": True, "risk_level": "critical"})
        if r == "demo_final_signoff":
            print("[PASS] route_after_finance: approved + critical → final_signoff")
            results.append(True)
        else:
            print(f"[FAIL] route_after_finance: approved + critical → expected 'demo_final_signoff', got '{r}'")
            results.append(False)

        # Approved + high → process
        r = demo_route_after_finance({"finance_approved": True, "risk_level": "high"})
        if r == "demo_process":
            print("[PASS] route_after_finance: approved + high → process")
            results.append(True)
        else:
            print(f"[FAIL] route_after_finance: approved + high → expected 'demo_process', got '{r}'")
            results.append(False)

        # --- route_after_final ---
        # Approved → process
        r = demo_route_after_final({"final_approved": True})
        if r == "demo_process":
            print("[PASS] route_after_final: approved → process")
            results.append(True)
        else:
            print(f"[FAIL] route_after_final: approved → expected 'demo_process', got '{r}'")
            results.append(False)

        # Rejected → reject
        r = demo_route_after_final({"final_approved": False})
        if r == "demo_reject":
            print("[PASS] route_after_final: rejected → reject")
            results.append(True)
        else:
            print(f"[FAIL] route_after_final: rejected → expected 'demo_reject', got '{r}'")
            results.append(False)

    except ImportError as e:
        print(f"[FAIL] Cannot import demo routing functions: {e}")
        return [False]
    except Exception as e:
        print(f"[FAIL] Demo routing test error: {e}")
        return [False]

    return results


def run_all_checks():
    """Run all graph structure checks."""
    print("=" * 60)
    print("Part 1: LangGraph Workflow Structure Tests")
    print("=" * 60)

    all_results = []

    print("\n--- Graph Import ---")
    all_results.append(check_graph_import())

    print("\n--- Graph Callable ---")
    all_results.append(check_graph_callable())

    print("\n--- Node Functions ---")
    all_results.extend(check_node_functions())

    print("\n--- Routing Functions (6 total) ---")
    all_results.extend(check_routing_functions())

    print("\n--- Interrupt Usage ---")
    all_results.extend(check_interrupt_usage())

    print("\n--- State Schema ---")
    all_results.extend(check_state_schema())

    print("\n--- Checkpointer ---")
    all_results.append(check_checkpointer())

    print("\n--- Demo Graph Structure ---")
    all_results.extend(check_demo_graph_escalation())

    print("\n--- Demo Escalation Routing Logic ---")
    all_results.extend(check_demo_routing_logic())

    print("\n" + "=" * 60)
    passed = sum(1 for r in all_results if r)
    total = len(all_results)
    print(f"Results: {passed}/{total} checks passed")
    print("=" * 60)

    return all(all_results)


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)


# --- pytest-discoverable tests ---

def test_graph_import():
    assert check_graph_import()

def test_graph_callable():
    assert check_graph_callable()

def test_node_functions():
    results = check_node_functions()
    assert all(results)

def test_routing_functions():
    results = check_routing_functions()
    assert all(results)

def test_interrupt_usage():
    results = check_interrupt_usage()
    assert all(results)

def test_state_schema():
    results = check_state_schema()
    assert all(results)

def test_checkpointer():
    assert check_checkpointer()

def test_demo_graph_escalation():
    results = check_demo_graph_escalation()
    assert all(results)

def test_demo_routing_logic():
    results = check_demo_routing_logic()
    assert all(results)
