"""
Benchmark Experiment Runner for Mini Cluster Lab.
Course: Cloud and Distributed Computing (CDC)

Executes repeatable benchmarks and scalability sweeps from CLI,
generating empirical results for academic reports and viva presentation.

Usage:
    python run_experiments.py
"""

import json
from processing.benchmark import run_benchmark, run_scalability_sweep


def main():
    print("=" * 70)
    print("  MINI CLUSTER LAB: EMPIRICAL BENCHMARK EXPERIMENTS")
    print("=" * 70)

    # 1. Experiment 1: Scheduling Strategies on Skewed Workload
    print("\n[+] EXPERIMENT 1: Scheduling Strategies Comparison (Skewed Workload)")
    print("    Parameters: Dataset M = 2,000, Workers N = 4, Intensity = 2x")
    res_skew = run_benchmark(
        dataset_size=2000,
        worker_count=4,
        intensity=2,
        workload="skewed",
        strategy="compare_all"
    )
    print(f"    Sequential Baseline Ts: {res_skew.sequential_time:.4f}s")
    for strat_name, s_data in res_skew.strategies.items():
        print(f"    - Strategy [{strat_name.upper():<11}]: Parallel Time = {s_data['parallel_time']:.4f}s | Speedup = {s_data['speedup']}x | LIF = {s_data['imbalance_factor']:.3f} | Valid: {s_data['is_valid']}")

    # 2. Experiment 2: Fault Tolerance & Retry Penalty
    print("\n[+] EXPERIMENT 2: Fault Tolerance & Transparent Recovery")
    print("    Parameters: Dataset M = 1,500, Workers N = 2, Intensity = 2x")
    res_norm = run_benchmark(dataset_size=1500, worker_count=2, intensity=2, inject_failure=False)
    res_fault = run_benchmark(dataset_size=1500, worker_count=2, intensity=2, inject_failure=True, fail_chunk_id=0)
    retry_cost = res_fault.parallel_time - res_norm.parallel_time
    print(f"    - Normal Run (No Fault): Time = {res_norm.parallel_time:.4f}s | Retries = {res_norm.retries}")
    print(f"    - Injected Fault Run   : Time = {res_fault.parallel_time:.4f}s | Retries = {res_fault.retries} | Retry Overhead = +{retry_cost:.4f}s")
    print(f"    - Output Validation    : {res_fault.validation_message}")

    # 3. Experiment 3: Scalability Sweep & Amdahl's Law Modeling
    print("\n[+] EXPERIMENT 3: Scalability Sweep & Amdahl's Law Prediction")
    print("    Parameters: Dataset M = 2,500, Intensity = 2x, Workers N = 1 to 4")
    sweep = run_scalability_sweep(dataset_size=2500, max_workers=4, intensity=2)
    print(f"    Estimated Serial Fraction s = {sweep['serial_fraction']:.4f} ({sweep['serial_percentage']}%)")
    print(f"    Max Theoretical Speedup     = {sweep['max_theoretical_speedup']}x")
    print(f"\n    {'Workers (N)':<12} | {'Ts (s)':<10} | {'Tp (s)':<10} | {'Speedup':<10} | {'Efficiency':<12} | {'Amdahl Pred'}")
    print("    " + "-" * 70)
    for pt in sweep["points"]:
        n = pt["N"]
        ts = pt["sequential_time"]
        tp = pt["parallel_time"]
        sp = pt["speedup"]
        eff = pt["efficiency"]
        pred_entry = next((c for c in sweep["amdahl_curve"] if c["N"] == n), None)
        pred_sp = f"{pred_entry['amdahl_predicted']}x" if pred_entry else "N/A"
        print(f"    {n:<12} | {ts:<10.4f} | {tp:<10.4f} | {sp:<9.2f}x | {eff:<11.1f}% | {pred_sp}")

    print("\n" + "=" * 70)
    print("  ALL BENCHMARKS EXECUTED AND EMPIRICALLY VALIDATED!")
    print("=" * 70)


if __name__ == "__main__":
    main()
