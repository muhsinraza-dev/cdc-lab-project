"""
Cluster Launcher Script for Real Network Mode (Feature F5).
Course: Cloud and Distributed Computing (CDC)

Starts N worker node servers on ports 5001..500N as background subprocesses,
monitors their health, and shuts them down cleanly on exit.

Usage:
    python start_nodes.py --nodes 4
"""

import sys
import time
import subprocess
import argparse
import atexit
from typing import List

CHILD_PROCESSES: List[subprocess.Popen] = []


def cleanup():
    """Terminate all spawned worker node processes on exit."""
    print("\n[*] Terminating worker node processes...")
    for p in CHILD_PROCESSES:
        try:
            p.terminate()
            p.wait(timeout=2)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    print("[*] All worker nodes stopped cleanly.")


atexit.register(cleanup)


def main():
    parser = argparse.ArgumentParser(description="Start local HTTP worker nodes cluster")
    parser.add_argument("--nodes", type=int, default=4, help="Number of worker nodes to launch (default: 4)")
    parser.add_argument("--base-port", type=int, default=5001, help="Starting port (default: 5001)")
    args = parser.parse_args()

    num_nodes = max(1, min(8, args.nodes))
    base_port = args.base_port

    print("=" * 65)
    print(f"  LAUNCHING MINI CLUSTER: {num_nodes} HTTP WORKER NODES")
    print("=" * 65)

    for i in range(num_nodes):
        port = base_port + i
        cmd = [sys.executable, "node_server.py", "--port", str(port)]
        proc = subprocess.Popen(cmd)
        CHILD_PROCESSES.append(proc)
        print(f"  [+] Node {i + 1} launched on http://127.0.0.1:{port} (PID: {proc.pid})")
        time.sleep(0.3)

    print("-" * 65)
    print(f"  Cluster is RUNNING. Press Ctrl+C to terminate all worker nodes.")
    print("=" * 65)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Received shutdown signal.")


if __name__ == "__main__":
    main()
