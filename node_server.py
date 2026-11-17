"""
Worker Node HTTP Server for Real Network Mode (Feature F5).
Course: Cloud and Distributed Computing (CDC)

Runs an individual HTTP worker node process listening on a designated TCP port.
Accepts computational chunk assignments over HTTP POST, computes them,
and returns serialized results and precise timing back to the coordinator.

Usage:
    python node_server.py --port 5001
"""

import os
import sys
import time
import argparse
from typing import Dict, Any

from flask import Flask, request, jsonify

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from processing.tasks import compute_task

node_app = Flask(__name__)
NODE_PORT = 5001


@node_app.route("/health", methods=["GET"])
def health():
    """Health check endpoint to verify node reachability."""
    return jsonify({
        "status": "healthy",
        "port": NODE_PORT,
        "pid": os.getpid(),
        "timestamp": time.time(),
    })


@node_app.route("/process", methods=["POST"])
def process_chunk():
    """
    Process an assigned computational chunk over HTTP.

    Payload:
        {
            "chunk_id": int,
            "items": [[orig_idx, val], ...],
            "intensity": int,
            "run_t0": float
        }
    """
    payload = request.get_json(silent=True) or {}
    chunk_id = payload.get("chunk_id", 0)
    items = payload.get("items", [])
    intensity = payload.get("intensity", 1)
    run_t0 = payload.get("run_t0", time.perf_counter())

    t_start = time.perf_counter() - run_t0
    pid = os.getpid()

    # Deterministic computation
    results = []
    for orig_idx, val in items:
        computed = compute_task(val, intensity)
        results.append([orig_idx, computed])

    t_end = time.perf_counter() - run_t0
    duration = max(0.0, t_end - t_start)

    return jsonify({
        "status": "success",
        "chunk_id": chunk_id,
        "worker_pid": pid,
        "node_port": NODE_PORT,
        "n_items": len(items),
        "results": results,
        "t_start": round(t_start, 5),
        "t_end": round(t_end, 5),
        "duration": round(duration, 5),
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Distributed Worker Node Server")
    parser.add_argument("--port", type=int, default=5001, help="Port to listen on (e.g. 5001)")
    args = parser.parse_args()
    NODE_PORT = args.port

    print(f"[*] Starting Worker Node on http://127.0.0.1:{NODE_PORT} (PID {os.getpid()})...")
    node_app.run(host="127.0.0.1", port=NODE_PORT, debug=False)
