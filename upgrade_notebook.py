"""
Upgrade script for notebooks/distributed_task_processing.ipynb.
Appends Mini Cluster Lab upgrade sections:
- Section 10: Scheduling Strategies & Load Imbalance under Skewed Workloads
- Section 11: Worker Execution Timeline & Utilization Analysis (Gantt Chart)
- Section 12: Fault Tolerance & Transparent Recovery Demonstration
- Section 13: Scalability Sweep & Amdahl's Law Curve Fitting
"""

import json

def upgrade_notebook():
    notebook_path = "notebooks/distributed_task_processing.ipynb"
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # Update Title
    nb["cells"][0]["source"][0] = "# Mini Cluster Lab: Distributed Task Processing & Performance Analysis System\n"

    new_cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 10. Mini Cluster Lab Upgrade: Scheduling Strategies & Load Imbalance\n",
                "\n",
                "In real-world distributed systems, workloads are rarely uniform. Under a **Skewed Workload**, task computational cost increases non-linearly.\n",
                "- **Static Scheduling:** Allocates equal item counts ($N$ chunks). The worker with the last chunk becomes a massive straggler, causing high Load Imbalance ($\text{LIF} = \max(busy) / \text{mean}(busy) \gg 1.0$).\n",
                "- **Dynamic Scheduling:** Partitions data into fine-grained chunks ($N \\times 4$). Workers pull chunks on-demand, allowing early-finishing workers to balance the load.\n",
                "- **Interleaved Scheduling:** Round-robin item assignment cyclically evens out monotonic skew.\n"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from processing.benchmark import run_benchmark\n",
                "import matplotlib.pyplot as plt\n",
                "\n",
                "# Run comparison across all strategies on skewed workload\n",
                "res_skew = run_benchmark(dataset_size=2000, worker_count=4, intensity=2, workload='skewed', strategy='compare_all')\n",
                "\n",
                "print(f'Sequential Baseline Time (Ts): {res_skew.sequential_time:.4f}s\\n')\n",
                "strategies = ['static', 'dynamic', 'interleaved']\n",
                "times = []\n",
                "lifs = []\n",
                "for s in strategies:\n",
                "    data = res_skew.strategies[s]\n",
                "    times.append(data['parallel_time'])\n",
                "    lifs.append(data['imbalance_factor'])\n",
                "    print(f\"{s.capitalize():<12} | {data['parallel_time']:12.4f} s | {data['speedup']:8.2f} x | {data['imbalance_factor']:6.3f} | {'Passed' if data['is_valid'] else 'Failed'}\")\n",
                "\n",
                "fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))\n",
                "ax1.bar(strategies, times, color=['#f43f5e', '#10b981', '#818cf8'])\n",
                "ax1.set_title('Execution Time by Strategy (Skewed Workload)')\n",
                "ax1.set_ylabel('Parallel Time (s)')\n",
                "ax1.grid(True, linestyle='--', alpha=0.3)\n",
                "\n",
                "ax2.bar(strategies, lifs, color=['#f43f5e', '#10b981', '#818cf8'])\n",
                "ax2.set_title('Load Imbalance Factor (LIF: 1.0 = Ideal)')\n",
                "ax2.set_ylabel('LIF Ratio')\n",
                "ax2.axhline(1.0, color='white', linestyle='--', alpha=0.6, label='Ideal Balance (1.0)')\n",
                "ax2.legend()\n",
                "ax2.grid(True, linestyle='--', alpha=0.3)\n",
                "plt.tight_layout()\n",
                "plt.show()\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 11. Mini Cluster Lab Upgrade: Worker Timeline & Utilization (Gantt Chart)\n",
                "\n",
                "By instrumenting workers with `time.perf_counter()` relative to the run start timestamp, the coordinator constructs an exact timeline showing chunk execution windows, busy times, and idle waiting gaps across worker processes."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Inspect the worker timeline from the dynamic scheduling run\n",
                "dyn_meta = res_skew.strategies['dynamic']\n",
                "timeline = dyn_meta['timeline']\n",
                "worker_stats = dyn_meta['worker_stats']\n",
                "\n",
                "fig, ax = plt.subplots(figsize=(12, 4))\n",
                "colors = ['#38bdf8', '#06b6d4', '#818cf8', '#10b981', '#f59e0b', '#ec4899']\n",
                "for bar in timeline:\n",
                "    worker_label = bar['worker_label']\n",
                "    t_start = bar['t_start']\n",
                "    dur = bar['duration']\n",
                "    c_id = bar['chunk_id']\n",
                "    ax.barh(worker_label, dur, left=t_start, height=0.55, color=colors[c_id % len(colors)], edgecolor='#0b0f19')\n",
                "\n",
                "ax.set_title('Worker Execution Timeline (Gantt Chart) - Dynamic Scheduling')\n",
                "ax.set_xlabel('Elapsed Time (Seconds from run start)')\n",
                "ax.grid(True, linestyle='--', alpha=0.3)\n",
                "plt.tight_layout()\n",
                "plt.show()\n",
                "\n",
                "for ws in worker_stats:\n",
                "    print(f\"{ws['worker_label']:<12} | PID: {ws['worker_pid']:<6} | Chunks: {ws['chunks_processed']:<3} | Busy: {ws['busy_time']:7.4f}s | Util: {ws['utilization_pct']:5.1f}%\")\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 12. Mini Cluster Lab Upgrade: Fault Tolerance & Transparent Recovery\n",
                "\n",
                "The coordinator intercepts simulated worker hardware/process faults (`SimulatedWorkerFailure`), preserves system state, and transparently resubmits the task to another free worker."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Execute benchmark with simulated worker failure injection\n",
                "res_fault = run_benchmark(dataset_size=1500, worker_count=2, intensity=2, inject_failure=True, fail_chunk_id=0)\n",
                "\n",
                "print(f\"Retries Handled      : {res_fault.retries}\")\n",
                "print(f\"Validation Outcome   : {res_fault.validation_message}\")\n",
                "print('\\n--- Coordinator Event Recovery Stream ---')\n",
                "for line in res_fault.event_log:\n",
                "    print(f\"> {line}\")\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 13. Mini Cluster Lab Upgrade: Scalability Sweep & Amdahl's Law Curve\n",
                "\n",
                "Amdahl's Law defines theoretical speedup $S(N) = 1 / [s + (1-s)/N]$. We execute an automated scalability sweep across worker counts, estimate the serial fraction $s$, and plot measured speedups against theoretical limits."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from processing.benchmark import run_scalability_sweep\n",
                "\n",
                "sweep = run_scalability_sweep(dataset_size=2000, max_workers=4, intensity=2)\n",
                "print(f\"Estimated Serial Fraction s : {sweep['serial_fraction']:.4f} ({sweep['serial_percentage']}%)\")\n",
                "print(f\"Max Theoretical Speedup (1/s): {sweep['max_theoretical_speedup']:.2f}x\\n\")\n",
                "\n",
                "workers = [p['N'] for p in sweep['points']]\n",
                "sp_measured = [p['speedup'] for p in sweep['points']]\n",
                "sp_ideal = [p['N'] for p in sweep['points']]\n",
                "sp_amdahl = [c['amdahl_predicted'] for c in sweep['amdahl_curve'] if c['N'] in workers]\n",
                "\n",
                "plt.figure(figsize=(10, 5))\n",
                "plt.plot(workers, sp_measured, 'o-', label='Measured Speedup', color='#06b6d4', linewidth=2.5)\n",
                "plt.plot(workers, sp_ideal, '--', label='Ideal Linear (S = N)', color='gray', alpha=0.6)\n",
                "plt.plot(workers, sp_amdahl, ':s', label=f\"Amdahl Prediction (s={sweep['serial_fraction']:.2f})\", color='#f59e0b', linewidth=2)\n",
                "plt.title(\"Scalability Analysis: Measured Speedup vs. Amdahl's Law\")\n",
                "plt.xlabel('Worker Process Count (N)')\n",
                "plt.ylabel('Speedup Factor')\n",
                "plt.legend()\n",
                "plt.grid(True, linestyle='--', alpha=0.3)\n",
                "plt.tight_layout()\n",
                "plt.show()\n"
            ]
        }
    ]

    nb["cells"].extend(new_cells)

    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)

    print("Successfully updated notebooks/distributed_task_processing.ipynb with all new sections!")

if __name__ == "__main__":
    upgrade_notebook()
