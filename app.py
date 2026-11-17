"""
Flask Web Application for "Mini Cluster Lab" —
Distributed Task Processing and Performance Analysis System.

Course: Cloud and Distributed Computing (CDC)

Serves the interactive performance dashboard, exposes API endpoints for:
- Task benchmark execution (Uniform / Skewed workloads, Static / Dynamic / Interleaved scheduling)
- Fault tolerance demonstration (worker failure injection and retry)
- Scalability sweep and Amdahl's Law mathematical prediction modeling
- Benchmark session history and CSV / JSON export data
"""

import os
import sys
import platform
from datetime import datetime
from typing import List, Dict, Any, Optional

from flask import Flask, render_template, request, jsonify

# Local processing package imports
from processing.benchmark import run_benchmark, run_scalability_sweep
from processing.metrics import BenchmarkMetrics

app = Flask(__name__)

# In-memory history for the current server session
BENCHMARK_HISTORY: List[Dict[str, Any]] = []

# System topology inspection
LOGICAL_CORES = os.cpu_count() or 4
MAX_SAFE_WORKERS = min(LOGICAL_CORES, 16)
MAX_SAFE_DATASET_SIZE = 25000
MAX_SAFE_INTENSITY = 10
MAX_SAFE_REPETITIONS = 5


@app.route("/")
def index():
    """Render the interactive Mini Cluster Lab dashboard."""
    sys_info = {
        "os": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "python_version": platform.python_version(),
        "cpu_cores": LOGICAL_CORES,
        "max_workers": MAX_SAFE_WORKERS,
    }
    return render_template("index.html", sys_info=sys_info)


@app.route("/api/system-info", methods=["GET"])
def system_info():
    """Return runtime host specifications and input constraints."""
    return jsonify({
        "status": "success",
        "system": {
            "os": f"{platform.system()} {platform.release()}",
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "logical_cpu_cores": LOGICAL_CORES,
            "max_workers_allowed": MAX_SAFE_WORKERS,
            "max_dataset_size": MAX_SAFE_DATASET_SIZE,
            "max_intensity": MAX_SAFE_INTENSITY,
            "max_repetitions": MAX_SAFE_REPETITIONS,
            "simulation_disclosure": (
                "Simulated cluster: worker processes on one machine, not multiple physical machines."
            ),
        }
    })


@app.route("/api/benchmark", methods=["POST"])
def execute_benchmark():
    """
    Run an end-to-end benchmark comparison between sequential and parallel execution.
    Supports workload types, scheduling strategies, and failure injection.
    """
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({
            "status": "error",
            "message": "Invalid request: JSON body required."
        }), 400

    # 1. Parameter Extraction & Sanitization
    try:
        raw_size = payload.get("dataset_size", 2000)
        raw_workers = payload.get("worker_count", min(4, LOGICAL_CORES))
        raw_intensity = payload.get("intensity", 2)
        raw_repetitions = payload.get("repetitions", 1)

        dataset_size = int(raw_size)
        worker_count = int(raw_workers)
        intensity = int(raw_intensity)
        repetitions = int(raw_repetitions)

        workload = str(payload.get("workload", "uniform")).lower().strip()
        if workload not in ["uniform", "skewed"]:
            workload = "uniform"

        strategy = str(payload.get("strategy", "static")).lower().strip()
        if strategy not in ["static", "dynamic", "interleaved", "compare_all"]:
            strategy = "static"

        inject_failure = bool(payload.get("inject_failure", False))
        raw_fail_chunk = payload.get("fail_chunk_id", 2)
        fail_chunk_id = int(raw_fail_chunk) if raw_fail_chunk is not None else 2

    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": "Parameters (dataset_size, worker_count, intensity, repetitions) must be valid integers."
        }), 400

    # Boundary checks
    if dataset_size < 10 or dataset_size > MAX_SAFE_DATASET_SIZE:
        return jsonify({
            "status": "error",
            "message": f"Dataset size must be between 10 and {MAX_SAFE_DATASET_SIZE} items."
        }), 400

    if worker_count < 1 or worker_count > MAX_SAFE_WORKERS:
        return jsonify({
            "status": "error",
            "message": f"Worker count must be between 1 and {MAX_SAFE_WORKERS} (limited by host CPU topology)."
        }), 400

    if intensity < 1 or intensity > MAX_SAFE_INTENSITY:
        return jsonify({
            "status": "error",
            "message": f"Workload intensity must be between 1 and {MAX_SAFE_INTENSITY}."
        }), 400

    if repetitions < 1 or repetitions > MAX_SAFE_REPETITIONS:
        return jsonify({
            "status": "error",
            "message": f"Repetitions must be between 1 and {MAX_SAFE_REPETITIONS}."
        }), 400

    # 2. Execution of Benchmark
    try:
        metric = run_benchmark(
            dataset_size=dataset_size,
            worker_count=worker_count,
            intensity=intensity,
            repetitions=repetitions,
            seed=42,
            warmup=False,
            workload=workload,
            strategy=strategy,
            inject_failure=inject_failure,
            fail_chunk_id=fail_chunk_id,
        )

        result_record = {
            "run_id": len(BENCHMARK_HISTORY) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "dataset_size": metric.dataset_size,
            "worker_count": metric.worker_count,
            "intensity": metric.intensity,
            "repetitions": metric.repetitions,
            "workload": metric.workload,
            "strategy": metric.strategy,
            "sequential_time": round(metric.sequential_time, 4),
            "parallel_time": round(metric.parallel_time, 4),
            "speedup": round(metric.speedup, 2) if metric.speedup is not None else None,
            "efficiency": round(metric.efficiency, 1) if metric.efficiency is not None else None,
            "imbalance_factor": metric.imbalance_factor,
            "is_valid": metric.is_valid,
            "validation_message": metric.validation_message,
            "timeline": metric.timeline,
            "worker_stats": metric.worker_stats,
            "overhead": metric.overhead,
            "event_log": metric.event_log,
            "retries": metric.retries,
            "strategies": metric.strategies,
        }

        # Store in session history
        BENCHMARK_HISTORY.append(result_record)

        return jsonify({
            "status": "success",
            "data": result_record
        })

    except Exception as e:
        print(f"[Benchmark Server Error]: {e}", file=sys.stderr)
        return jsonify({
            "status": "error",
            "message": f"An internal error occurred during benchmark execution: {str(e)}"
        }), 500


@app.route("/api/scalability", methods=["POST"])
def execute_scalability():
    """
    Run an automated scalability sweep across worker counts (N = 1..max_workers),
    measure speedup, fit Amdahl's Law serial fraction, and return theoretical curve.
    """
    payload = request.get_json(silent=True) or {}
    try:
        dataset_size = int(payload.get("dataset_size", 2000))
        max_workers = int(payload.get("max_workers", min(8, LOGICAL_CORES)))
        intensity = int(payload.get("intensity", 2))
        workload = str(payload.get("workload", "uniform")).lower().strip()
        strategy = str(payload.get("strategy", "dynamic")).lower().strip()
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": "Invalid parameter types for scalability sweep."
        }), 400

    dataset_size = max(100, min(dataset_size, 10000))
    max_workers = max(1, min(max_workers, min(8, LOGICAL_CORES)))
    intensity = max(1, min(intensity, 5))

    try:
        sweep_data = run_scalability_sweep(
            dataset_size=dataset_size,
            max_workers=max_workers,
            intensity=intensity,
            workload=workload,
            strategy=strategy,
        )
        return jsonify({
            "status": "success",
            "data": sweep_data
        })
    except Exception as e:
        print(f"[Scalability Sweep Error]: {e}", file=sys.stderr)
        return jsonify({
            "status": "error",
            "message": f"Scalability sweep error: {str(e)}"
        }), 500


@app.route("/api/history", methods=["GET"])
def get_history():
    """Retrieve history of all runs performed in this session."""
    return jsonify({
        "status": "success",
        "count": len(BENCHMARK_HISTORY),
        "history": BENCHMARK_HISTORY
    })


@app.route("/api/history/clear", methods=["POST"])
def clear_history():
    """Clear benchmark session history."""
    global BENCHMARK_HISTORY
    BENCHMARK_HISTORY = []
    return jsonify({
        "status": "success",
        "message": "Benchmark history cleared."
    })


if __name__ == "__main__":
    import argparse
    import socket

    def is_port_in_use(p: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", p)) == 0

    parser = argparse.ArgumentParser(description="Mini Cluster Lab Dashboard Server")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 5000)), help="Port to listen on (default: 5000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address to bind to (default: 127.0.0.1)")
    args = parser.parse_args()

    port = args.port
    if is_port_in_use(port) and args.port == 5000:
        print(f"  [!] Port {port} is occupied by another process. Auto-switching to port 5050...")
        port = 5050

    print("=" * 65)
    print("  CDC DISTRIBUTED TASK PROCESSING — MINI CLUSTER LAB")
    print("=" * 65)
    print(f"  Host Architecture : {platform.system()} ({LOGICAL_CORES} Logical Cores)")
    print(f"  Simulation Mode   : Single-machine multi-process coordinator-worker")
    print(f"  Server URL        : http://{args.host}:{port}")
    print("=" * 65)
    app.run(host=args.host, port=port, debug=False)
