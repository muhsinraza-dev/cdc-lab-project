# UPGRADE_PLAN.md
# "Mini Cluster Lab" — Upgrade of the Distributed Task Processing Project

> **Instruction to the coding agent:** The base project from `PROJECT_PLAN.md` already works
> (dataset size, worker count, workload multiplier, repetitions, sequential vs parallel, speedup,
> efficiency, correctness validation, two charts). **Do NOT rewrite or break it.** Add the features
> below on top of the existing code, in priority order. Finish and test each feature before the next.
> Deadline is ONE day, so keep everything simple, readable and defensible in a viva.

---

## 1. Idea in one line

Turn the project from "a benchmark button" into a **small cluster lab** that does not only say
*"parallel is faster"* but shows **WHY**: how work is scheduled across workers, what happens when a
worker fails, and where the theoretical limit of speedup comes from (Amdahl's Law).

These are the exact topics a Cloud & Distributed Computing teacher asks about:
**load balancing, scheduling, fault tolerance, scalability limits, overhead.**

## 2. Rules (unchanged and important)

- All numbers, charts and tables come from **real measured runs**. Never hardcode results.
- Everything runs on one machine, so label it honestly in the UI:
  *"Simulated cluster: worker processes on one machine, not multiple physical machines."*
  (Exception: Feature F5, only if done, uses separate HTTP node servers; still label localhost honestly.)
- No database, login, API keys, paid services or heavy frontend frameworks.
- Keep the same stack: Python, Flask, `multiprocessing` / `concurrent.futures`, Chart.js on the frontend.
- Add comments explaining each new function in simple English.

---

## 3. Features (priority order)

### F1 — Worker Timeline (Gantt chart)  ⏱ ~1.5 h  **MUST**

**What:** After a parallel run, show a horizontal timeline: one row per worker, one coloured bar per
chunk, positioned by real start/end time. Idle gaps are visible. This makes the coordinator/worker
model visible during the demo.

**How:**
- Change the worker function so each chunk returns, besides its results, a metadata dict:
  `{chunk_id, worker_pid, n_items, t_start, t_end}`. Use `time.perf_counter()` values converted to
  seconds relative to the run start (`run_t0` is passed to the worker, or use `time.time()` relative
  to a recorded start).
- Map `worker_pid` to labels `Worker 1..N` (order of first appearance).
- Aggregator returns `timeline: [...]` in the JSON response.
- Frontend: render with Chart.js floating horizontal bars (`indexAxis: 'y'`, data as `[start, end]`),
  x-axis = seconds, y-axis = workers.
- Also compute **per-worker busy time** and **utilization % = busy / total parallel time**.

**Acceptance:** timeline shows N rows for N workers, bars never overlap within one worker, and total
span ≈ parallel time.

---

### F2 — Scheduling Strategy Comparison + Load Imbalance  ⏱ ~2 h  **MUST**

**What:** Compare how work is *divided*, which is the core of load balancing.

Add a "Workload type" selector:
- **Uniform** — every item costs about the same (current behaviour).
- **Skewed** — item cost grows with its value (e.g. cost proportional to `x`), and the dataset is
  generated sorted, so the last chunk is much heavier than the first. This creates a real imbalance.

Add a "Scheduling strategy" selector (and an option "Compare all"):
1. **Static** — split into exactly N equal chunks, one per worker (`Pool.map` with N chunks).
2. **Dynamic** — split into many small chunks (e.g. `N * 8`), workers take the next chunk when free
   (`Pool.imap_unordered`). Re-order results by `chunk_id` before validation.
3. *(optional)* **Round-robin / interleaved** — item `i` goes to worker `i % N`.

**Metrics to show:**
- Parallel time per strategy.
- **Load imbalance factor = max(worker busy time) / mean(worker busy time)** (1.0 = perfect balance).
- Speedup and efficiency per strategy.
- Correctness validation for each strategy (must be exact match with sequential).

**Frontend:** grouped bar chart (strategies x time) plus the F1 timeline for the selected strategy.
With Skewed workload, static should visibly show one worker working long while others sit idle, and
dynamic should look balanced. **Report whatever is actually measured, even if the result is
surprising.**

---

### F3 — Fault Tolerance Demo (simulated failure + retry)  ⏱ ~1.5 h  **MUST**

**What:** A checkbox "Inject worker failure". The coordinator survives a failing chunk and still
produces a correct result.

**How (keep it simple and safe, do NOT kill OS processes):**
- Worker receives `(chunk, chunk_id, attempt)`. If failure injection is on and
  `chunk_id == fail_chunk_id` and `attempt == 0`, the worker **raises** `SimulatedWorkerFailure`.
- Coordinator submits chunks with `apply_async` (or `ProcessPoolExecutor.submit`), catches the
  exception, logs it, and **resubmits** that chunk (max 2 retries).
- Produce an **event log**: `chunk 3 failed on attempt 0 -> retried -> succeeded on attempt 1`.
- Show the log in the UI, plus "retries used", "total time with failure vs without failure" (retry cost).
- Validation must still pass 100%.

**Label clearly:** "Failure is simulated by raising an exception inside a worker."

---

### F4 — Scalability Analysis + Amdahl's Law  ⏱ ~2 h  **MUST**

**What:** One button "Run scalability sweep": run the same workload with N = 1, 2, 3, 4 ... up to
`os.cpu_count()` (cap at 8), repeating each configuration.

**Compute from real data:**
- Speedup `S(N) = Ts / Tp(N)` and efficiency `E(N) = S(N)/N`.
- Estimated **serial fraction** `s` from each point:
  `s = (1/S - 1/N) / (1 - 1/N)` for N > 1, then take the median.
- **Amdahl prediction:** `S_amdahl(N) = 1 / (s + (1 - s)/N)`.
- Show the **maximum theoretical speedup** `1/s` (when `s > 0`).

**Chart (this also fixes the current half-empty "Speedup vs Ideal Linear" chart):**
Line chart with 3 lines over N: **Measured**, **Ideal linear** (`S = N`), **Amdahl prediction**.
Plus an efficiency line or table.

**Also add a simple "overhead breakdown"** per run: time spent in (a) partitioning, (b) parallel
compute + communication, (c) aggregation + validation. Show as a stacked bar. Measure each with
`perf_counter`.

---

### F5 — Real Network Mode ("nodes" as HTTP servers)  ⏱ ~3 h  **OPTIONAL, only if F1–F4 are done and tested**

**What:** The most "distributed" upgrade. Start N tiny worker **node servers** (each its own
process/port, e.g. 5001–5004). The coordinator sends chunks to nodes as JSON over HTTP and
collects results. This adds *real* serialization and network overhead.

**How:**
- `node_server.py`: tiny Flask app with `POST /process` (takes `{chunk, workload}`, returns results +
  timing) and `GET /health`. Port from command line: `python node_server.py --port 5001`.
- `network_coordinator.py`: use `ThreadPoolExecutor` to POST chunks to the nodes in parallel with
  `requests` (timeout + retry on connection failure, re-routing to another node).
- `start_nodes.py`: launches N nodes as subprocesses and stops them on exit.
- Dashboard: mode selector **"Multiprocessing" vs "HTTP nodes"**, and a chart comparing the two
  (expected: network mode has extra overhead; report only measured values).
- Node addresses configurable in a list, so with two laptops on the same Wi-Fi the teacher could use
  real IPs. Default stays `127.0.0.1`.
- Honest label: "Nodes run on localhost. Replace addresses with real machines to test a true cluster."

---

## 4. API changes

Extend `POST /api/benchmark` (keep old fields working). Validate all of it server-side.

```json
{
  "dataset_size": 3000,
  "workers": 4,
  "intensity": 5,
  "repetitions": 2,
  "workload": "uniform | skewed",
  "strategy": "static | dynamic | compare_all",
  "inject_failure": false,
  "fail_chunk_id": 2
}
```

Response additions: `timeline[]`, `worker_stats[]` (busy time, utilization), `imbalance_factor`,
`strategies{}` (per-strategy results), `event_log[]`, `retries`, `overhead{partition, compute, aggregate}`.

New endpoint: `POST /api/scalability` -> `{points: [{N, Ts, Tp, speedup, efficiency}], serial_fraction,
max_speedup, amdahl_curve: [...]}`.

Safe limits: dataset size and intensity capped; workers capped at `max(1, cpu_count)` (or 8);
return clear JSON error messages (HTTP 400) for bad input.

## 5. UI changes

- Keep the current dark dashboard style and the left control panel.
- Add tabs: **Benchmark | Timeline | Scheduling | Fault Tolerance | Scalability (Amdahl)**.
- Fix display bug: labels currently show raw LaTeX like `$M$`, `$T_p$`, `$S$`, `\times 100\%`.
  Replace with plain text: "Dataset size (M items)", "Parallel time (Tp)", "Speedup (S)", "Efficiency (E)".
- Add small "What am I seeing?" one-line explanation under each new chart (helps the demo).
- Add buttons: **Export results (CSV)** and **Export JSON** of the last run (cheap, looks professional).
- Keep the visible simulation-honesty banner.
- Add a loading state while a benchmark/sweep runs (sweeps take longer).

## 6. Tests (add to `tests/test_processing.py`)

- Static, dynamic and interleaved strategies each produce results identical to the sequential run.
- Order is preserved after `imap_unordered` re-ordering.
- Retry logic: with an injected failure the final result is still exact and `retries >= 1`.
- Skewed workload generator is deterministic (fixed seed).
- Amdahl helper: known inputs give the known serial fraction (unit-test the formula).
- Imbalance factor equals 1.0 for perfectly equal busy times.
- Edge cases: dataset smaller than worker count, empty dataset, workers = 1.

## 7. One-day schedule

| Time | Task |
|---|---|
| Hour 0–1 | Read existing code, fix LaTeX labels, add worker metadata (F1 backend) |
| Hour 1–2.5 | F1 timeline frontend + utilization |
| Hour 2.5–4.5 | F2 strategies + skewed workload + imbalance |
| Hour 4.5–6 | F3 failure injection + retry log |
| Hour 6–8 | F4 sweep + Amdahl chart + overhead breakdown |
| Hour 8–9 | Tests, README update, CSV/JSON export |
| Hour 9–10 | Report/slides additions (section 8), rehearse demo |
| Spare | F5 only if everything above is green |

If time runs short, **cut F5 first, then the overhead breakdown**. F1–F4 are the core of the upgrade.

## 8. Report / presentation additions

Update `reports/report_draft.md` and `reports/presentation_outline.md`:
- New headings: Scheduling and Load Balancing, Fault Tolerance, Scalability and Amdahl's Law.
- Each result table/graph must use real numbers from the final runs. Leave placeholders for team
  names; do not invent references or results.
- Demo script (about 5 min): 1) normal run, 2) show timeline, 3) skewed workload with static, then
  dynamic, 4) inject failure and show retry log, 5) scalability sweep and Amdahl chart.
- Add Viva Q&A: What is load balancing? Static vs dynamic scheduling? What is Amdahl's Law? Why does
  efficiency drop as workers increase? How does the coordinator handle failure? Is this a true
  distributed system and why not? How would you extend to real machines?

## 9. Final deliverable from the agent

- Summary of files created or changed.
- Commands to install, test and run.
- Test results (do not hide failures).
- What was NOT completed (for example F5), stated honestly.
- Checklist of what the students must personalize before submission.
