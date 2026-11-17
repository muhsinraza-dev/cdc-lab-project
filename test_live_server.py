"""
Live Server Integration and End-to-End Verification Test.
Course: Cloud and Distributed Computing (CDC)

Tests all REST endpoints on http://127.0.0.1:5000:
1. Web Page Delivery (GET /)
2. System Specifications (GET /api/system-info)
3. Standard Uniform Benchmark (POST /api/benchmark)
4. Skewed Workload with Compare All Strategies (POST /api/benchmark)
5. Fault Tolerance & Automatic Retry (POST /api/benchmark)
6. Amdahl's Law Scalability Sweep (POST /api/scalability)
7. Session History Logging & Persistence (GET /api/history)
"""

import urllib.request
import urllib.error
import json
import time

import os
import sys
import argparse

BASE_URL = os.environ.get("BASE_URL", "")


def get_base_url():
    global BASE_URL
    if BASE_URL:
        return BASE_URL
    for port in [5000, 5050]:
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/api/system-info")
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if "system" in data:
                    BASE_URL = f"http://127.0.0.1:{port}"
                    return BASE_URL
        except Exception:
            pass
    BASE_URL = "http://127.0.0.1:5000"
    return BASE_URL


def make_request(path, method="GET", body=None):
    base = get_base_url()
    url = f"{base}{path}"
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read().decode("utf-8")
        try:
            return resp.status, json.loads(content)
        except json.JSONDecodeError:
            return resp.status, content


def main():
    parser = argparse.ArgumentParser(description="Live server test")
    parser.add_argument("--url", type=str, default="", help="Base URL of server")
    parser.add_argument("--port", type=int, default=None, help="Server port")
    args = parser.parse_args()

    global BASE_URL
    if args.url:
        BASE_URL = args.url.rstrip("/")
    elif args.port:
        BASE_URL = f"http://127.0.0.1:{args.port}"
    else:
        BASE_URL = get_base_url()

    print("=" * 70)
    print(f"  TESTING LIVE MINI CLUSTER LAB SERVER ({BASE_URL})")
    print("=" * 70)

    # 1. Test GET /
    print("\n[1/7] Testing Web Interface (GET /)...")
    status, html = make_request("/")
    assert status == 200, f"Expected 200, got {status}"
    assert "Mini Cluster Lab" in html, "Page title/branding not found in HTML"
    assert "Worker Timeline" in html, "Worker Timeline tab not found in HTML"
    assert "Scheduling &amp; Load Balancing" in html or "Scheduling" in html, "Scheduling tab missing"
    assert "Fault Tolerance" in html, "Fault tolerance tab missing"
    assert "Scalability (Amdahl's Law)" in html or "Amdahl" in html, "Amdahl tab missing"
    print("  -> PASSED: Dashboard HTML served successfully (Length: {} bytes)".format(len(html)))

    # 2. Test GET /api/system-info
    print("\n[2/7] Testing Host System Diagnostics (GET /api/system-info)...")
    status, sys_info = make_request("/api/system-info")
    assert status == 200
    sys_data = sys_info["system"]
    print(f"  -> Host OS        : {sys_data['os']} ({sys_data['machine']})")
    print(f"  -> Python Version : {sys_data['python_version']}")
    print(f"  -> CPU Topology   : {sys_data['logical_cpu_cores']} Logical Cores")
    print(f"  -> Max Workers    : {sys_data['max_workers_allowed']}")
    print(f"  -> Disclosure     : {sys_data['simulation_disclosure']}")
    print("  -> PASSED: System diagnostics verified.")

    # 3. Test POST /api/benchmark (Uniform, Static)
    print("\n[3/7] Testing Benchmark Endpoint (Uniform, Static, N=4, M=1500)...")
    payload1 = {
        "dataset_size": 1500,
        "worker_count": 4,
        "intensity": 2,
        "repetitions": 1,
        "workload": "uniform",
        "strategy": "static",
        "inject_failure": False,
    }
    t0 = time.time()
    status, res1 = make_request("/api/benchmark", method="POST", body=payload1)
    dur1 = time.time() - t0
    assert status == 200, res1
    b1 = res1["data"]
    print(f"  -> Sequential Time Ts : {b1['sequential_time']:.4f}s")
    print(f"  -> Parallel Time Tp   : {b1['parallel_time']:.4f}s")
    print(f"  -> Speedup (S)        : {b1['speedup']}x")
    print(f"  -> Efficiency (E)     : {b1['efficiency']}%")
    print(f"  -> Imbalance (LIF)    : {b1['imbalance_factor']}")
    print(f"  -> Validation         : {b1['validation_message']}")
    print(f"  -> Timeline Bars      : {len(b1['timeline'])} chunks tracked")
    print(f"  -> Worker Stats Rows  : {len(b1['worker_stats'])} workers active")
    assert b1["is_valid"] is True
    assert len(b1["timeline"]) > 0
    print("  -> PASSED: Uniform benchmark executed and validated.")

    # 4. Test POST /api/benchmark (Skewed, Compare All Strategies)
    print("\n[4/7] Testing Skewed Workload & Compare All Strategies Mode (N=4, M=2000)...")
    payload2 = {
        "dataset_size": 2000,
        "worker_count": 4,
        "intensity": 2,
        "repetitions": 1,
        "workload": "skewed",
        "strategy": "compare_all",
        "inject_failure": False,
    }
    t0 = time.time()
    status, res2 = make_request("/api/benchmark", method="POST", body=payload2)
    dur2 = time.time() - t0
    assert status == 200, res2
    b2 = res2["data"]
    strats = b2["strategies"]
    print(f"  -> Sequential Time Ts : {b2['sequential_time']:.4f}s")
    for s_name in ["static", "dynamic", "interleaved"]:
        s_data = strats[s_name]
        print(f"     * [{s_name.upper():<11}] Time: {s_data['parallel_time']:.4f}s | Speedup: {s_data['speedup']}x | LIF: {s_data['imbalance_factor']:.3f} | Valid: {s_data['is_valid']}")
        assert s_data["is_valid"] is True
    print("  -> PASSED: All 3 strategies compared, executed, and 100% validated.")

    # 5. Test POST /api/benchmark (Fault Tolerance & Retry Recovery)
    print("\n[5/7] Testing Fault Tolerance & Transparent Retry Resubmission...")
    payload3 = {
        "dataset_size": 1200,
        "worker_count": 2,
        "intensity": 2,
        "repetitions": 1,
        "workload": "uniform",
        "strategy": "static",
        "inject_failure": True,
        "fail_chunk_id": 0,
    }
    status, res3 = make_request("/api/benchmark", method="POST", body=payload3)
    assert status == 200, res3
    b3 = res3["data"]
    print(f"  -> Injected Exception : SimulatedWorkerFailure on chunk #0")
    print(f"  -> Retries Handled    : {b3['retries']}")
    print(f"  -> Output Validated   : {b3['is_valid']}")
    print(f"  -> Event Log Stream   :")
    for log_msg in b3["event_log"]:
        print(f"     > {log_msg}")
    assert b3["retries"] >= 1, "Expected at least 1 retry"
    assert b3["is_valid"] is True, "Output must be valid despite failure"
    print("  -> PASSED: Fault recovery successfully caught exception and reconstructed valid output.")

    # 6. Test POST /api/scalability (Amdahl's Law Sweep)
    print("\n[6/7] Testing Scalability Sweep & Amdahl's Law Curve (N=1..4)...")
    payload4 = {
        "dataset_size": 1800,
        "max_workers": 4,
        "intensity": 2,
        "workload": "uniform",
        "strategy": "dynamic",
    }
    status, res4 = make_request("/api/scalability", method="POST", body=payload4)
    assert status == 200, res4
    sc = res4["data"]
    print(f"  -> Estimated Serial Fraction s : {sc['serial_fraction']} ({sc['serial_percentage']}%)")
    print(f"  -> Max Theoretical Speedup     : {sc['max_theoretical_speedup']}x")
    print(f"  -> Empirical Points Measured   : {len(sc['points'])}")
    for pt in sc["points"]:
        print(f"     * N={pt['N']} Workers: Ts={pt['sequential_time']:.4f}s | Tp={pt['parallel_time']:.4f}s | Speedup={pt['speedup']}x | Eff={pt['efficiency']}%")
    print(f"  -> Amdahl Curve Data Points    : {len(sc['amdahl_curve'])}")
    print(f"  -> Stage Overhead Breakdowns   : {len(sc['overhead_breakdown'])}")
    assert len(sc["points"]) == 4
    assert len(sc["amdahl_curve"]) >= 4
    print("  -> PASSED: Scalability sweep and theoretical Amdahl modeling verified.")

    # 7. Test GET /api/history
    print("\n[7/7] Testing Session Experiment History (GET /api/history)...")
    status, hist = make_request("/api/history")
    assert status == 200
    runs = hist["history"]
    print(f"  -> Total Runs Recorded in Session: {hist['count']}")
    for r in runs:
        print(f"     * Run #{r['run_id']}: M={r['dataset_size']}, N={r['worker_count']}, Strategy={r['strategy']}, Speedup={r['speedup']}x, Valid={r['is_valid']}")
    assert hist["count"] >= 3
    print("  -> PASSED: Session history successfully logged all experimental runs.")

    print("\n" + "=" * 70)
    print("  ALL 7 SERVER TESTS PASSED PERFECTLY! THE PROJECT IS RUNNING 100%!")
    print("=" * 70)


if __name__ == "__main__":
    main()
