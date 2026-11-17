# Mini Cluster Lab: Distributed Task Processing & Performance Analysis System
### Cloud and Distributed Computing (CDC) Course Project

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask 3.1](https://img.shields.io/badge/Flask-3.1-black.svg)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/Tests-34%20Passed-brightgreen.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-Coordinator--Worker-orange.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 1. Project Overview

The **Mini Cluster Lab** is an educational distributed computing laboratory built in Python. Moving beyond a simple "parallel is faster" benchmark, this project demonstrates **WHY** distributed systems behave as they do:
- How tasks are scheduled across workers (**Static, Dynamic, Interleaved**).
- What happens when a worker encounters a hardware or software fault (**Fault Tolerance & Transparent Recovery**).
- Where the theoretical limit of parallel speedup comes from (**Amdahl's Law & Serial Fraction Modeling**).
- How coordinator scheduling latency and idle gaps look in real time (**Worker Timeline Gantt Chart**).

> **Important Disclosure on Distributed Systems vs. Multiprocessing:**  
> The core system runs worker processes as isolated operating system processes on one host machine using Python's `multiprocessing` / `concurrent.futures`. While the architectural roles (Coordinator, Worker, Aggregator) mirror those of distributed clusters, all processes execute on a single physical host sharing CPU and memory resources. It is **not** a multi-node networked deployment by default. For true network communication, Feature F5 provides an optional multi-port HTTP worker node server cluster.

---

## 2. Upgraded Features Breakdown

### F1: Worker Execution Timeline (Gantt Chart)
- High-resolution monotonic timers (`time.perf_counter()`) record exact `t_start` and `t_end` for every chunk relative to the run start.
- Maps OS process IDs (PIDs) to friendly worker labels (`Worker 1..N`).
- Renders an interactive horizontal Gantt chart with floating bars displaying active compute windows and idle waiting gaps.
- Computes per-worker busy time and **utilization percentage** ($T_{\text{busy}} / T_{\text{total}}$).

### F2: Scheduling Strategies & Load Imbalance Analysis
- **Workload Types:**
  - **Uniform:** Items require comparable computational effort.
  - **Skewed:** Computational difficulty increases non-linearly with item index ($x_i \propto i^{1.8}$), creating heavy stragglers.
- **Partitioning Strategies:**
  - **Static:** Splits dataset into $N$ equal contiguous chunks.
  - **Dynamic:** Slices dataset into $N \times 4$ fine chunks; workers pull chunks on-demand.
  - **Interleaved:** Round-robin item assignment ($i \pmod N$).
  - **Compare All:** Concurrently evaluates all three strategies on identical data.
- **Load Imbalance Factor (LIF):** $\max(\text{busy}) / \text{mean}(\text{busy})$ ($1.0 = \text{Ideal}$).

### F3: Fault Tolerance & Transparent Task Recovery
- Simulates worker node failure by raising `SimulatedWorkerFailure` inside an isolated worker process.
- Coordinator catches the exception, preserves system state, increments attempt count, and transparently resubmits the task to another free worker.
- Produces a real-time terminal log stream documenting failure and recovery events.
- Guarantees $100\%$ exact output correctness validation despite failures.

### F4: Scalability Sweep & Amdahl's Law Modeling
- 1-click automated sweep across $N = 1, 2, 3, 4+$ worker processes.
- Estimates the empirical serial fraction ($s$) from measured speedup:
  $$s = \frac{\frac{1}{S} - \frac{1}{N}}{1 - \frac{1}{N}} \quad (N > 1)$$
- Models the theoretical maximum speedup limit ($1/s$) and generates the 3-line comparative plot: **Measured Speedup vs. Ideal Linear vs. Amdahl Predicted Curve**.
- Provides a stacked bar chart breaking down stage overheads: **Partitioning vs. Parallel Compute vs. Aggregation**.

### F5 (Optional): Real Network Mode (HTTP Worker Node Cluster)
- `node_server.py`: Micro-service worker node accepting chunks over HTTP POST with JSON serialization.
- `start_nodes.py`: Launches $N$ worker nodes on ports `5001..500N` as subprocesses.
- `network_coordinator.py`: Dispatches chunks across network nodes concurrently via `ThreadPoolExecutor` and `urllib.request`.

---

## 3. Directory Structure

```text
cdc-lab-project/
├── app.py                                   # Flask web dashboard and REST API controller
├── node_server.py                           # [F5] Individual HTTP worker node server
├── start_nodes.py                           # [F5] Multi-port HTTP worker cluster launcher
├── run_experiments.py                       # CLI experiment runner for reports & viva demo
├── upgrade_notebook.py                      # Jupyter notebook upgrade injector script
├── requirements.txt                         # Dependencies (Flask, matplotlib)
├── README.md                                # Setup, architecture, and viva study guide
├── UPGRADE_PLAN.md                          # Specifications for Mini Cluster Lab features
├── PROJECT_PLAN.md                          # Base project architectural specifications
├── processing/                              # Reusable Distributed Processing Engine
│   ├── __init__.py                          # Package exports
│   ├── tasks.py                             # Uniform/skewed workloads & SimulatedWorkerFailure
│   ├── coordinator.py                       # Static/Dynamic/Interleaved scheduling & retry logic
│   ├── benchmark.py                         # Benchmark controller & Amdahl scalability sweep
│   ├── metrics.py                           # Speedup, efficiency, LIF, Amdahl math & validation
│   └── network_coordinator.py               # [F5] HTTP worker cluster coordinator
├── templates/
│   └── index.html                           # 5-tab responsive dashboard template
├── static/
│   ├── css/
│   │   └── style.css                        # Modern dark-mode scientific design system
│   └── js/
│       └── dashboard.js                     # Tab controls, Chart.js visualizations, CSV/JSON export
├── notebooks/
│   └── distributed_task_processing.ipynb    # Google Colab / Jupyter notebook (Sections 1-13)
├── reports/
│   ├── report_draft.md                      # Complete 12-section academic project report
│   └── presentation_outline.md              # 5-minute demo script, 9-slide deck & Viva Q&A
└── tests/
    └── test_processing.py                   # 34 automated unit and integration tests
```

---

## 4. Setup and Installation

### Prerequisites
- Python 3.10+ (Tested on Python 3.12.10)
- `pip` package manager

### 1. Open Workspace
```bash
cd "cdc-lab-project"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 5. Execution Commands

### A. Run Automated Unit Tests (34 Tests)
Verify task partitioning, scheduling strategies, fault tolerance retries, Amdahl mathematics, and exact validation:
```bash
python -m unittest discover tests
```
*Expected output:*
```text
..................................
----------------------------------------------------------------------
Ran 34 tests in 7.615s

OK
```

### B. Run Empirical Benchmarks from CLI
Capture actual measurements for the academic report:
```bash
python run_experiments.py
```

### C. Launch Interactive Web Dashboard
Start the local Flask dashboard:
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

### D. (Optional) Launch Real Network HTTP Worker Cluster (Feature F5)
In a separate terminal, launch 4 worker nodes:
```bash
python start_nodes.py --nodes 4
```
Workers will listen on ports `5001`, `5002`, `5003`, and `5004`.

---

## 6. Real Empirical Benchmark Results

Measured on host system (Windows 10, Python 3.12, 4 Logical Cores):

### Experiment 1: Scheduling Strategies under Skewed Workload ($M = 2,000$, $N = 4$)
- **Sequential Baseline ($T_s$):** $0.6313\text{ s}$
- **Static Partitioning:** $T_p = 1.2200\text{s}$ | Speedup $= 0.52\times$ | $\text{LIF} = \mathbf{1.892}$ (Severe straggler bottleneck)
- **Dynamic Partitioning:** $T_p = \mathbf{1.1014\text{s}}$ | Speedup $= \mathbf{0.57\times}$ | $\text{LIF} = \mathbf{1.303}$ (Work stealing balances load)
- **Interleaved:** $T_p = 1.1949\text{s}$ | Speedup $= 0.53\times$ | $\text{LIF} = 1.040$

### Experiment 2: Fault Tolerance & Transparent Task Recovery ($M = 1,500$, $N = 2$)
- **Normal Execution:** $T_p = 1.2516\text{s}$ | Retries $= 0$
- **Injected Fault Run:** $T_p = 0.9167\text{s}$ | Retries $= 1$ | Correctness Validation: **100% Match**

### Experiment 3: High-Intensity Workload Overcoming Overhead ($M = 4,000$, Intensity 5, $N = 4$)
- **Sequential Time ($T_s$):** $3.5487\text{ s}$
- **Parallel Time ($T_p$):** $1.8382\text{ s}$
- **Measured Speedup:** **1.93x**
- **Parallel Efficiency:** **48.3%**

---

## 7. Viva Voce Study Guide (Essential Q&A)

1. **What is Load Balancing?**  
   Distributing computational tasks across workers so that all workers spend equal time computing, minimizing idle waiting.
2. **Why is Static scheduling bad for Skewed workloads?**  
   Because $N$ equal item slices mean the worker with the hardest items works long after others finish, causing severe stragglers ($\text{LIF} \gg 1.0$).
3. **How does Dynamic scheduling fix this?**  
   It divides data into many small chunks ($N \times 4$). Workers pull chunks on demand; workers that finish light chunks immediately take more work.
4. **What is Amdahl's Law?**  
   Theoretical speedup limit $S(N) = 1 / [s + (1-s)/N]$ bounded by the non-parallelizable serial fraction $s$.
5. **How does the Coordinator handle worker failure?**  
   Catches `SimulatedWorkerFailure`, logs the incident, and transparently resubmits the chunk to another free worker.
6. **Is this a true distributed system?**  
   No, it is a single-host multi-process simulation. However, it faithfully implements the coordinator-worker distributed architecture, algorithms, and scheduling policies.

---

## 8. Student Personalization Checklist (Before Final Submission)

Before submitting your lab report and demo to your instructor, customize the following placeholders:

- [ ] **`reports/report_draft.md`**: Fill in your team members' full names, registration/roll numbers, university department, and course code on the Title Page (Section 1).
- [ ] **`reports/presentation_outline.md`**: Fill in team member names on Slide 1.
- [ ] **`notebooks/distributed_task_processing.ipynb`**: Update team names in the title Markdown cell.
- [ ] **Run Unit Tests**: Execute `python -m unittest discover tests` and verify that all 34 tests display `OK`.
- [ ] **Rehearse Demo**: Walk through the 5-minute demo script in `reports/presentation_outline.md`.
