"""
test_api.py — Self-Healing Retail Pricing Platform
Quick smoke test for all Flask API endpoints.

Usage:
    python test_api.py               # runs all tests against localhost:5001
    python test_api.py --url http://x.x.x.x:5001   # custom host
"""

import sys
import argparse
import requests

# ── Colours (cross-platform safe) ────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

PASS = f"{GREEN}  PASS{RESET}"
FAIL = f"{RED}  FAIL{RESET}"
SKIP = f"{YELLOW}  SKIP{RESET}"


def banner(text):
    print(f"\n{CYAN}{BOLD}{'─'*55}")
    print(f"  {text}")
    print(f"{'─'*55}{RESET}")


def result(name, ok, detail=""):
    icon = PASS if ok else FAIL
    detail_str = f"  → {detail}" if detail else ""
    print(f"{icon}  {name}{detail_str}")
    return ok


# =========================
# Test 1: Health Check
# =========================
def test_health(base_url):
    banner("1. GET /health")
    try:
        r = requests.get(f"{base_url}/health", timeout=5)
        ok = r.status_code == 200
        data = r.json()
        result("Status 200",        ok,                        f"got {r.status_code}")
        result("status == 'ok'",    data.get("status") == "ok", str(data.get("status")))
        result("model_loaded field", "model_loaded" in data,   str(data))
        return ok
    except requests.exceptions.ConnectionError:
        print(f"{RED}  ERROR: Cannot connect to {base_url}  —  is Flask running?{RESET}")
        return False


# =========================
# Test 2: Optimize — basic
# =========================
def test_optimize_basic(base_url):
    banner("2. POST /optimize  (basic)")
    payload = {"price": 100, "day": 2, "month": 5}
    try:
        r = requests.post(f"{base_url}/optimize", json=payload, timeout=10)
        ok = r.status_code == 200
        if not ok:
            result("Status 200", False, f"got {r.status_code}: {r.text}")
            return False

        data = r.json()
        result("Status 200",            True)
        result("current_price present",  "current_price"   in data, str(data.get("current_price")))
        result("best_price present",     "best_price"      in data, str(data.get("best_price")))
        result("best_revenue present",   "best_revenue"    in data, str(data.get("best_revenue")))
        result("improvement_% present",  "improvement_%"   in data, str(data.get("improvement_%")))
        result("decision present",       "decision"        in data, str(data.get("decision")))
        result("best_price >= 0",        data.get("best_price", -1) >= 0)
        result("best_revenue >= 0",      data.get("best_revenue", -1) >= 0)
        return True
    except Exception as e:
        print(f"{RED}  ERROR: {e}{RESET}")
        return False


# =========================
# Test 3: Optimize — with optional fields
# =========================
def test_optimize_with_extras(base_url):
    banner("3. POST /optimize  (with stock + competitor_price)")
    payload = {
        "price": 150,
        "day": 4,
        "month": 11,
        "stock": 30,
        "competitor_price": 140.0
    }
    try:
        r = requests.post(f"{base_url}/optimize", json=payload, timeout=10)
        ok = r.status_code == 200
        if not ok:
            result("Status 200", False, f"got {r.status_code}: {r.text}")
            return False

        data = r.json()
        result("Status 200",               True)
        result("competitor_price echoed",  "competitor_price" in data,  str(data.get("competitor_price")))
        result("decision is a string",     isinstance(data.get("decision"), str), data.get("decision"))

        valid_decisions = {
            "Apply Optimized Price",
            "Keep Current Price",
            "Consider Competitive Pricing (Competitor is cheaper)"
        }
        result("decision is valid",        data.get("decision") in valid_decisions, data.get("decision"))
        return True
    except Exception as e:
        print(f"{RED}  ERROR: {e}{RESET}")
        return False


# =========================
# Test 4: Optimize — edge cases
# =========================
def test_optimize_edge_cases(base_url):
    banner("4. POST /optimize  (edge cases & validation)")

    cases = [
        ("Missing 'price'",  {"day": 1, "month": 3},                  400),
        ("Missing 'day'",    {"price": 100, "month": 3},               400),
        ("Missing 'month'",  {"price": 100, "day": 1},                 400),
        ("day out of range", {"price": 100, "day": 9, "month": 3},     400),
        ("month out of range",{"price": 100, "day": 1, "month": 13},   400),
        ("Low price £1",     {"price": 1,   "day": 0, "month": 1},     200),
        ("High price £500",  {"price": 500, "day": 6, "month": 12},    200),
    ]

    all_ok = True
    for name, payload, expected_status in cases:
        try:
            r = requests.post(f"{base_url}/optimize", json=payload, timeout=10)
            ok = r.status_code == expected_status
            all_ok = all_ok and ok
            result(f"{name}  (expect {expected_status})", ok, f"got {r.status_code}")
        except Exception as e:
            result(name, False, str(e))
            all_ok = False

    return all_ok


# =========================
# Test 5: Reload Model
# =========================
def test_reload_model(base_url):
    banner("5. POST /reload_model")
    try:
        r = requests.post(f"{base_url}/reload_model", timeout=10)
        # No token set → should succeed (token protection is optional)
        ok = r.status_code in (200, 401)
        result(f"Status 200 or 401", ok, f"got {r.status_code}")
        if r.status_code == 200:
            result("model reloaded response", r.json().get("status") == "model reloaded",
                   str(r.json()))
        elif r.status_code == 401:
            print(f"{YELLOW}    (401 = RELOAD_TOKEN is set — that's fine){RESET}")
        return ok
    except Exception as e:
        print(f"{RED}  ERROR: {e}{RESET}")
        return False


# =========================
# Test 6: Revenue sanity
# =========================
def test_revenue_sanity(base_url):
    banner("6. Revenue sanity  (optimised >= current)")
    try:
        payload = {"price": 200, "day": 3, "month": 7}
        r = requests.post(f"{base_url}/optimize", json=payload, timeout=10)
        if r.status_code != 200:
            result("Request ok", False, f"got {r.status_code}")
            return False

        data = r.json()
        cur_rev  = data.get("current_revenue", 0)
        best_rev = data.get("best_revenue", 0)
        ok = best_rev >= cur_rev
        result("best_revenue >= current_revenue", ok,
               f"£{best_rev:.2f} vs £{cur_rev:.2f}")
        return ok
    except Exception as e:
        print(f"{RED}  ERROR: {e}{RESET}")
        return False


# =========================
# Main
# =========================
def main():
    parser = argparse.ArgumentParser(description="Smoke-test the Retail Pricing API.")
    parser.add_argument("--url", default="http://127.0.0.1:5001",
                        help="Base URL of the Flask API (default: http://127.0.0.1:5001)")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")

    print(f"\n{BOLD}{'='*55}")
    print(f"  Self-Healing Retail Pricing Platform — API Tests")
    print(f"  Target: {base_url}")
    print(f"{'='*55}{RESET}")

    tests = [
        test_health,
        test_optimize_basic,
        test_optimize_with_extras,
        test_optimize_edge_cases,
        test_reload_model,
        test_revenue_sanity,
    ]

    results = []
    for test_fn in tests:
        if not results or results[-1]:   # stop early only on connection error
            passed = test_fn(base_url)
            results.append(passed)
        else:
            # connection failed — skip remaining
            print(f"{SKIP}  {test_fn.__name__}  (skipped — API not reachable)")
            results.append(None)

    # ── Summary ──────────────────────────────────────────
    total   = len([r for r in results if r is not None])
    passed  = sum(1 for r in results if r is True)
    failed  = sum(1 for r in results if r is False)
    skipped = sum(1 for r in results if r is None)

    print(f"\n{BOLD}{'='*55}")
    print(f"  Results: {GREEN}{passed} passed{RESET}  "
          f"{RED}{failed} failed{RESET}  "
          f"{YELLOW}{skipped} skipped{RESET}")
    print(f"{'='*55}{RESET}\n")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
