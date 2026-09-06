import importlib.util
import json
import os
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = "/logs/verifier"


def load_test_module():
    spec = importlib.util.spec_from_file_location(
        "test_outputs", os.path.join(HERE, "test_outputs.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_all_tests(mod):
    """Runs every test_* function in the module. No pytest dependency: a test
    passes if it returns without raising, fails on any exception."""
    results = {}
    errors = {}
    for name in dir(mod):
        if not name.startswith("test_"):
            continue
        fn = getattr(mod, name)
        if not callable(fn):
            continue
        try:
            fn()
            results[name] = True
        except Exception:
            results[name] = False
            errors[name] = traceback.format_exc()
    return results, errors


def main():
    os.makedirs(LOG_DIR, exist_ok=True)

    load_error = None
    try:
        mod = load_test_module()
        results, errors = run_all_tests(mod)
    except Exception:
        results, errors = {}, {}
        load_error = traceback.format_exc()

    with open(os.path.join(HERE, "test_weights.json")) as f:
        weights = json.load(f)

    earned = 0.0
    positive_total = 0.0
    ctrf_tests = []
    weighted_names = {row["test_name"] for row in weights}

    for row in weights:
        name = row["test_name"]
        w = row["weight"]
        passed = results.get(name, False)
        if w > 0:
            positive_total += w
            if passed:
                earned += w
        else:
            if passed:
                earned += w  # negative weight subtracts from numerator
        ctrf_tests.append({
            "name": name,
            "status": "passed" if passed else "failed",
            "weight": w,
            "decision": bool(row.get("decision", False)),
            "error": None if passed else (errors.get(name) or load_error),
        })

    for name, passed in results.items():
        if name not in weighted_names:
            positive_total += 1
            if passed:
                earned += 1
            ctrf_tests.append({
                "name": name, "status": "passed" if passed else "failed",
                "weight": 1, "decision": False,
                "error": None if passed else errors.get(name),
            })

    reward = earned / positive_total if positive_total > 0 else 0.0
    reward = max(0.0, min(1.0, reward))

    with open(os.path.join(LOG_DIR, "reward.json"), "w") as f:
        json.dump({"reward": reward}, f)

    ctrf = {
        "results": {
            "tool": {"name": "retail-category-discontinuation-v1-verifier"},
            "summary": {
                "tests": len(ctrf_tests),
                "passed": sum(1 for t in ctrf_tests if t["status"] == "passed"),
                "failed": sum(1 for t in ctrf_tests if t["status"] == "failed"),
                "start": int(time.time()),
                "stop": int(time.time()),
            },
            "tests": ctrf_tests,
        }
    }
    with open(os.path.join(LOG_DIR, "ctrf.json"), "w") as f:
        json.dump(ctrf, f, indent=2)

    print(f"Reward (tests only): {reward:.4f}  ({earned}/{positive_total})")
    for t in ctrf_tests:
        mark = "PASS" if t["status"] == "passed" else "FAIL"
        print(f"  [{mark}] {t['name']} (weight {t['weight']})")


if __name__ == "__main__":
    main()
