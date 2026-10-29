"""
Test harness for Part 3: CopilotKit Frontend.

Verifies frontend configuration, package dependencies,
and CopilotKit component usage in source files.
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


def check_package_json_exists():
    """Verify package.json exists."""
    path = os.path.join(FRONTEND_DIR, "package.json")
    if os.path.exists(path):
        print("[PASS] package.json exists")
        return True
    else:
        print("[FAIL] package.json not found")
        return False


def check_copilotkit_dependencies():
    """Verify CopilotKit packages are in dependencies."""
    path = os.path.join(FRONTEND_DIR, "package.json")
    try:
        with open(path) as f:
            pkg = json.load(f)

        deps = pkg.get("dependencies", {})
        required = ["@copilotkit/react-core", "@copilotkit/react-ui"]
        results = []

        for dep in required:
            if dep in deps:
                print(f"[PASS] '{dep}' found in dependencies")
                results.append(True)
            else:
                print(f"[FAIL] '{dep}' not found in dependencies")
                results.append(False)

        return results
    except FileNotFoundError:
        print("[FAIL] package.json not found")
        return [False]
    except json.JSONDecodeError:
        print("[FAIL] package.json is not valid JSON")
        return [False]


def check_page_has_copilot_chat():
    """Verify page.tsx contains CopilotChat."""
    path = os.path.join(FRONTEND_DIR, "src", "app", "page.tsx")
    try:
        with open(path) as f:
            source = f.read()

        if "CopilotChat" in source:
            print("[PASS] page.tsx contains 'CopilotChat'")
            return True
        else:
            # Part 3 is GIVEN, so a missing CopilotChat means the provided UI is broken
            print("[FAIL] page.tsx does not contain 'CopilotChat'")
            return False
    except FileNotFoundError:
        print("[FAIL] page.tsx not found")
        return False


def check_approval_panel_has_interrupt():
    """Verify ApprovalPanel.tsx contains useLangGraphInterrupt."""
    path = os.path.join(FRONTEND_DIR, "src", "components", "ApprovalPanel.tsx")
    try:
        with open(path) as f:
            source = f.read()

        if "useLangGraphInterrupt" in source:
            print("[PASS] ApprovalPanel.tsx contains 'useLangGraphInterrupt'")
            return True
        else:
            # Part 3 is GIVEN, so a missing useLangGraphInterrupt means the provided UI is broken
            print("[FAIL] ApprovalPanel.tsx does not contain 'useLangGraphInterrupt'")
            return False
    except FileNotFoundError:
        print("[FAIL] ApprovalPanel.tsx not found")
        return False


def check_route_has_langgraph_agent():
    """Verify route.ts contains LangGraphHttpAgent or LangGraphAgent."""
    path = os.path.join(FRONTEND_DIR, "src", "app", "api", "copilotkit", "route.ts")
    try:
        with open(path) as f:
            source = f.read()

        if "LangGraphHttpAgent" in source or "LangGraphAgent" in source:
            print("[PASS] route.ts contains LangGraph agent integration")
            return True
        else:
            print("[FAIL] route.ts does not contain LangGraph agent integration")
            return False
    except FileNotFoundError:
        print("[FAIL] route.ts not found")
        return False


def check_layout_has_copilotkit():
    """Verify layout.tsx contains CopilotKit provider."""
    path = os.path.join(FRONTEND_DIR, "src", "app", "layout.tsx")
    try:
        with open(path) as f:
            source = f.read()

        if "CopilotKit" in source:
            print("[PASS] layout.tsx contains 'CopilotKit'")
            return True
        else:
            print("[FAIL] layout.tsx does not contain 'CopilotKit'")
            return False
    except FileNotFoundError:
        print("[FAIL] layout.tsx not found")
        return False


def check_next_config_exists():
    """Verify next.config.js exists."""
    path = os.path.join(FRONTEND_DIR, "next.config.js")
    if os.path.exists(path):
        print("[PASS] next.config.js exists")
        return True
    else:
        print("[FAIL] next.config.js not found")
        return False


def check_tsconfig_exists():
    """Verify tsconfig.json exists."""
    path = os.path.join(FRONTEND_DIR, "tsconfig.json")
    if os.path.exists(path):
        print("[PASS] tsconfig.json exists")
        return True
    else:
        print("[FAIL] tsconfig.json not found")
        return False


def check_tailwind_config_exists():
    """Verify tailwind.config.ts exists."""
    path = os.path.join(FRONTEND_DIR, "tailwind.config.ts")
    if os.path.exists(path):
        print("[PASS] tailwind.config.ts exists")
        return True
    else:
        print("[FAIL] tailwind.config.ts not found")
        return False


def check_types_file():
    """Verify types.ts exists and has key types."""
    path = os.path.join(FRONTEND_DIR, "src", "lib", "types.ts")
    try:
        with open(path) as f:
            source = f.read()

        checks = []
        for type_name in ["FinancialRequest", "ApprovalDecision", "InterruptData", "RiskLevel"]:
            if type_name in source:
                print(f"[PASS] types.ts defines '{type_name}'")
                checks.append(True)
            else:
                print(f"[FAIL] types.ts missing '{type_name}'")
                checks.append(False)

        return checks
    except FileNotFoundError:
        print("[FAIL] types.ts not found")
        return [False]


def run_all_checks():
    """Run all frontend checks."""
    print("=" * 60)
    print("Part 3: CopilotKit Frontend Tests")
    print("=" * 60)

    all_results = []

    print("\n--- Package Configuration ---")
    all_results.append(check_package_json_exists())
    copilotkit_results = check_copilotkit_dependencies()
    all_results.extend(copilotkit_results)

    print("\n--- Component Source Checks ---")
    all_results.append(check_page_has_copilot_chat())
    all_results.append(check_approval_panel_has_interrupt())
    all_results.append(check_route_has_langgraph_agent())
    all_results.append(check_layout_has_copilotkit())

    print("\n--- Config Files ---")
    all_results.append(check_next_config_exists())
    all_results.append(check_tsconfig_exists())
    all_results.append(check_tailwind_config_exists())

    print("\n--- TypeScript Types ---")
    type_results = check_types_file()
    all_results.extend(type_results)

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

def test_package_json_exists():
    assert check_package_json_exists()

def test_copilotkit_dependencies():
    results = check_copilotkit_dependencies()
    assert all(results)

def test_page_has_copilot_chat():
    assert check_page_has_copilot_chat()

def test_approval_panel_has_interrupt():
    assert check_approval_panel_has_interrupt()

def test_route_has_langgraph_agent():
    assert check_route_has_langgraph_agent()

def test_layout_has_copilotkit():
    assert check_layout_has_copilotkit()

def test_next_config_exists():
    assert check_next_config_exists()

def test_tsconfig_exists():
    assert check_tsconfig_exists()

def test_tailwind_config_exists():
    assert check_tailwind_config_exists()

def test_types_file():
    results = check_types_file()
    assert all(results)
