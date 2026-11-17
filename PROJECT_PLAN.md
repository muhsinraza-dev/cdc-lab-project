# PROJECT_PLAN.md
# Distributed Task Processing and Performance Analysis System

## 1. Project Overview

**Project title:** Distributed Task Processing and Performance Analysis System Using Python

**Course:** Cloud and Distributed Computing (CDC)  
**Team size:** 3 students  
**Difficulty:** Intermediate  
**Target completion time:** 2–3 days  
**Primary language:** Python  
**Development tools:** Google Colab, Python, Flask, multiprocessing, Matplotlib, Pandas (optional)

### Project summary

Build an educational software system that demonstrates how a large computational workload can be split into smaller chunks, processed by multiple worker processes, and combined by a coordinator. Compare sequential processing against parallel processing and visualize the measured performance.

The project should have:
1. A simple web dashboard for running experiments and viewing results.
2. A Google Colab notebook for repeatable experiments and course demonstration.
3. A reusable Python processing engine shared by the notebook and web app.
4. Automatically generated tables and graphs.
5. A report draft and presentation outline based on actual implementation and measured results.

### Important accuracy requirement

A single machine running multiple Python processes demonstrates **parallel processing / a distributed-processing simulation**, not a true multi-machine distributed system. The initial version must clearly disclose this in the UI and report. Do not claim that separate physical or networked machines are being used unless a real multi-machine version is implemented and tested.

The project must be software-only. No hardware, paid cloud account, external database, or API key should be required.

---

## 2. Goals and Learning Outcomes

The finished project should allow a student to:
- Understand task partitioning and result aggregation.
- Compare sequential and parallel execution.
- Experiment with different dataset sizes and worker counts.
- Measure elapsed time, speedup, and parallel efficiency.
- Validate that sequential and parallel outputs are equivalent.
- Discuss process-startup overhead and why parallel execution is not always faster.
- Explain the distinction between multiprocessing on one machine and distributed processing across networked machines.

### Performance formulas

Let:
- `Ts` = sequential execution time in seconds.
- `Tp` = parallel execution time in seconds.
- `N` = number of worker processes.

Speedup:

`Speedup = Ts / Tp`

Parallel efficiency:

`Efficiency (%) = (Ts / (N * Tp)) * 100`

Handle zero or near-zero timings safely. Display `N/A` or a clear explanation if a value cannot be calculated reliably.

Do not hardcode or fabricate benchmark results. All charts, tables, and report result fields must come from actual experiment output.

---

## 3. Scope and Time Management

### Must-have features
1. Sequential baseline implementation.
2. Parallel processing with Python `multiprocessing`.
3. Coordinator that splits a workload into chunks.
4. Worker function that processes assigned chunks.
5. Result aggregation and correctness validation.
6. Measurement of elapsed time.
7. Experiments across several dataset sizes and worker counts.
8. Charts for execution time and speedup.
9. Simple Flask web dashboard.
10. Google Colab notebook using the same core logic where practical.
11. README with setup/run instructions.
12. Report draft and presentation outline.

### Optional features (only after all must-haves work)
- CSV export of benchmark results.
- Downloadable JSON results.
- A small task-history table saved in a local JSON or CSV file.
- A simulated worker-failure explanation or controlled demonstration.
- A separate-machine worker architecture proposal in the future-work section.

Do not spend time on authentication, user accounts, MongoDB, payment, deployment, or complex frontend frameworks. They are not needed for this CDC project and would increase risk within the time limit.

---

## 4. Workload Definition

Use a deterministic, CPU-oriented educational workload so results are repeatable and sequential/parallel results can be compared.

### Recommended task

For each integer `x` in a generated input dataset, calculate a deterministic computational result, such as the sum of squares from `1` to `x`, or another equivalent CPU-bound operation.

Requirements:
- Use a fixed random seed if random values are generated.
- Keep input generation separate from timed processing, unless explicitly testing end-to-end time.
- Validate that sequential and parallel results match exactly.
- Explain that extremely simple work can be dominated by multiprocessing overhead.
- Allow configurable workload intensity, within safe bounds, so experiments are long enough to measure.

### Suggested experiment matrix

Use sensible, configurable defaults such as:
- Dataset sizes: small, medium, and large.
- Worker counts: 1, 2, and 4, limited by available CPU resources.
- Repeat each configuration at least 3 times if time allows.
- Report average execution time and optionally minimum/standard deviation.
- Run a warm-up or explain any first-run overhead.

Do not assume more workers always means faster execution. The program must display measured outcomes, even if parallel execution is slower.

---

## 5. Architecture

### Logical architecture

`User`
  -> `Flask Web Dashboard`
  -> `Experiment Controller`
  -> `Coordinator / Task Splitter`
  -> `Worker Processes`
  -> `Result Aggregator`
  -> `Validation + Metrics Calculator`
  -> `Results Table + Charts`

The Colab notebook imports or reproduces the same processing functions in a notebook-friendly way and performs the same benchmark experiments.

### Component responsibilities

#### A. Web dashboard
- Presents project title and concise explanation.
- Offers input controls for dataset size, worker count, repetitions, and workload intensity.
- Starts a benchmark after validating inputs.
- Displays sequential time, parallel time, speedup, efficiency, and correctness status.
- Displays charts and a results table.
- Shows a visible note: “Initial version uses multiple processes on one machine; this is not a multi-machine distributed deployment.”
- Shows helpful error messages if a run fails.

#### B. Experiment controller
- Validates request parameters.
- Calls the benchmark functions.
- Measures elapsed time.
- Prepares results in a JSON-serializable structure for the web interface.

#### C. Coordinator
- Divides the input into reasonably balanced chunks.
- Assigns chunks to worker processes.
- Collects completed outputs.
- Preserves correct ordering where necessary.
- Handles empty/small input safely.

#### D. Worker
- Accepts one chunk.
- Processes each input deterministically.
- Returns results and, if useful, a small amount of metadata.
- Does not write to shared output files concurrently.

#### E. Result aggregator and validator
- Combines worker results.
- Checks output length and exact equality against the sequential result.
- Marks the run as successful only if validation passes.

#### F. Metrics module
- Measures elapsed time with `time.perf_counter()`.
- Calculates speedup and efficiency safely.
- Aggregates repeated runs.
- Avoids rounding until values are displayed.

#### G. Visualization module
- Produces a sequential-versus-parallel execution-time chart.
- Produces a speedup chart across worker counts or dataset sizes.
- Labels axes, units, and chart titles.
- Uses actual benchmark data, never example values as if they were real.

---

## 6. Recommended Project Structure

Create this structure:

```text
distributed-task-processing/
├── app.py
├── processing/
│   ├── __init__.py
│   ├── tasks.py
│   ├── coordinator.py
│   ├── benchmark.py
│   └── metrics.py
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── dashboard.js
├── notebooks/
│   └── distributed_task_processing.ipynb
├── results/
│   └── .gitkeep
├── reports/
│   ├── report_draft.md
│   └── presentation_outline.md
├── tests/
│   └── test_processing.py
├── requirements.txt
├── README.md
└── PROJECT_PLAN.md
```

Keep the project simple. If the timeline becomes tight, prioritize a working core engine and notebook before polishing the web interface.

---

## 7. Technology Requirements

### Python
Use a recent stable Python version supported by Flask and the selected dependencies.

### Flask
Use Flask to serve the dashboard and expose a small endpoint that starts a benchmark and returns JSON results.

### multiprocessing
Use `multiprocessing` or `concurrent.futures.ProcessPoolExecutor` for CPU-bound parallel work. Pick one approach and use it consistently. Prefer a straightforward, reliable implementation over unnecessary abstractions.

Important cross-platform rules:
- Put the runnable web app behind `if __name__ == "__main__":`.
- Keep worker functions at module level so they can be pickled.
- Test on the actual operating system.
- Do not assume multiprocessing behaves identically in Google Colab, Windows, and Linux.
- If multiprocessing inside the Flask request handler is unreliable in a given environment, run experiments through the notebook/CLI and let the dashboard show saved benchmark results. Document the limitation rather than pretending it works.

### Matplotlib
Use it to create graphs. Charts may be rendered as PNG files or converted to base64 for the web page. Keep chart creation separate from core processing logic.

### Requirements
Include only the dependencies actually used, for example:
- Flask
- matplotlib
- pandas (only if needed)

Python standard-library modules should be preferred when sufficient.

---

## 8. Web Application Requirements

Build a clean, responsive, professional educational dashboard. It is a local web app, not a production cloud service.

### Page layout

#### Header
- Project title.
- Subtitle: “Explore task partitioning and parallel performance.”
- Small status label indicating “Local simulation”.

#### Project overview panel
Explain:
- What the coordinator does.
- What workers do.
- Why sequential and parallel performance is compared.
- The single-machine simulation limitation.

#### Experiment controls
Provide:
- Dataset size selection (safe preset options plus validated custom input).
- Worker count selection, limited to reasonable values and available CPU count.
- Repetitions (for example, 1–5).
- Workload intensity, bounded to prevent extremely long runs.
- “Run Benchmark” button.
- “Reset” button.

#### Results summary
Show cards for:
- Sequential execution time (seconds).
- Parallel execution time (seconds).
- Speedup.
- Parallel efficiency.
- Correctness validation status.

#### Charts
Show:
1. Sequential vs parallel execution time.
2. Speedup by worker count or dataset size.

#### Results table
Include:
- Dataset size.
- Worker count.
- Sequential time.
- Parallel time.
- Speedup.
- Efficiency.
- Validation result.

#### User feedback
- Display a loading state while a benchmark runs.
- Disable duplicate submissions during a run.
- Display validation errors in plain language.
- Do not expose raw stack traces to the browser.
- Never claim a run succeeded until it actually completes.

### Design guidance
- Use a restrained academic/scientific visual style.
- Make labels readable on a classroom projector.
- Avoid excessive animations.
- Use semantic HTML and accessible form labels.
- Ensure the main page works on laptop screens and is usable on smaller screens.
- Do not build a complex React application; plain HTML, CSS, and JavaScript are sufficient.

---

## 9. Google Colab Notebook Requirements

Create `notebooks/distributed_task_processing.ipynb`.

Suggested notebook sections:
1. Project title, team names placeholders, and learning objectives.
2. Explanation of sequential, parallel, and distributed-processing concepts.
3. Imports and environment information.
4. Input data generation.
5. Sequential implementation.
6. Worker implementation.
7. Coordinator/chunk-splitting implementation.
8. Parallel execution.
9. Correctness validation.
10. Benchmark helper functions.
11. Experiments across dataset sizes.
12. Experiments across worker counts.
13. Results table.
14. Execution-time chart.
15. Speedup and efficiency chart.
16. Discussion of overhead and surprising results.
17. Limitations and conclusion.

Notebook quality requirements:
- Cells must run in order from top to bottom in Google Colab.
- Include brief Markdown explanations before important code sections.
- Avoid relying on files that exist only on the developer's computer.
- If multiprocessing restrictions arise in the notebook environment, implement a clear fallback for demonstration and disclose it.
- Do not fabricate outputs or screenshot results that have not been generated.
- Keep the notebook reproducible and suitable for a live class demo.

---

## 10. Implementation Plan for the Coding Agent

Follow this order and do not skip testing.

### Step 1 — Inspect the environment
- Check Python version and available project directory.
- Create the project structure.
- Avoid deleting or overwriting unrelated user files.

### Step 2 — Implement the core engine first
- Implement deterministic input generation.
- Implement sequential processing.
- Implement worker-level processing.
- Implement chunk partitioning and coordination.
- Implement result aggregation.
- Implement exact correctness validation.
- Add clear docstrings and basic type hints.

### Step 3 — Implement benchmark and metrics
- Use `time.perf_counter()`.
- Separate input generation from processing timing.
- Measure sequential and parallel versions.
- Repeat experiments when configured.
- Calculate mean timings, speedup, and efficiency.
- Save results in a consistent dictionary/list format.

### Step 4 — Test the core engine
Test:
- Empty input.
- One input item.
- Dataset smaller than worker count.
- Dataset evenly divisible by worker count.
- Dataset not evenly divisible by worker count.
- One worker.
- Multiple workers.
- Exact sequential/parallel output equivalence.
- Invalid parameters.
- Safe upper bounds on dataset size and workload.

### Step 5 — Build the Colab notebook
- Reuse the same processing logic where practical.
- Provide explanatory Markdown.
- Generate real result tables and charts.
- Verify that notebook cells run in order.

### Step 6 — Build the Flask web app
- Implement a dashboard route.
- Implement a benchmark endpoint.
- Validate all incoming parameters server-side.
- Return JSON with measurements and validation status.
- Display results and charts.
- Handle errors and prevent unsafe input sizes.

### Step 7 — Add reports and documentation
- Write setup and run instructions.
- Create a report draft that uses placeholders for team details and actual measurements.
- Create a presentation outline.
- Include limitations and ethical accuracy about simulation vs true distributed deployment.

### Step 8 — Final quality check
- Run all tests.
- Run one small benchmark and one larger benchmark.
- Confirm all results are actual, not hardcoded.
- Confirm graphs have labels and units.
- Confirm the dashboard communicates the simulation limitation.
- Confirm README commands work in a fresh environment.
- List any incomplete features honestly.

---

## 11. Testing and Acceptance Criteria

The project is considered complete when:
- [ ] Sequential processing runs.
- [ ] Parallel worker processing runs in the supported environment.
- [ ] Coordinator splits work and aggregates results.
- [ ] Sequential and parallel results match exactly.
- [ ] Timing uses a monotonic high-resolution timer.
- [ ] Speedup and efficiency calculations are correct.
- [ ] At least two workload sizes are tested.
- [ ] At least two worker configurations are tested where supported.
- [ ] At least one graph is generated from actual results; preferably both required graphs.
- [ ] Colab notebook has clear instructions and runs from top to bottom.
- [ ] Flask dashboard runs locally and validates inputs.
- [ ] README contains setup, run, testing, and troubleshooting instructions.
- [ ] Report includes architecture, methodology, actual results, discussion, limitations, and references.
- [ ] No fabricated benchmark values or unsupported claims are present.
- [ ] Every team member can explain the coordinator, workers, metrics, and limitations.

---

## 12. Report Draft Structure

Create `reports/report_draft.md` with these headings and useful draft text. Use placeholders for information that is not known. Do not invent team members, instructor names, institutional requirements, or experiment results.

1. Title Page
   - Project title
   - Course: Cloud and Distributed Computing
   - Student names and roll numbers
   - Instructor
   - Department / university
   - Submission date

2. Abstract
   - Problem, approach, tools, experiment methodology, and a placeholder for actual findings.

3. Introduction
   - Define task processing and explain why parallel/distributed techniques are studied.
   - Distinguish concurrency, parallelism, and distributed computing accurately.

4. Problem Statement
   - Explain the limitations of processing a computational workload sequentially and the motivation for partitioning work.

5. Objectives
   - Sequential baseline, worker-based processing, coordinator, validation, timing, performance analysis, and visualization.

6. Scope and Limitations
   - Educational single-machine multiprocessing simulation; not a production cluster.

7. Related Concepts / Background
   - Coordinator-worker model, task partitioning, result aggregation, process overhead, speedup, efficiency.
   - Include references to official Python documentation and credible academic/educational sources.

8. System Design
   - Architecture diagram, component responsibilities, workflow/flowchart.

9. Methodology
   - Dataset generation, workload, worker configurations, repetitions, measurement approach, validation.

10. Implementation
    - Technologies, key functions, UI, notebook structure.

11. Results and Discussion
    - Actual measurements only.
    - Results table, graphs, interpretation, cases where parallel processing is slower, possible overhead sources.

12. Testing
    - Test cases and pass/fail outcomes.

13. Limitations and Future Work
    - Single-machine limitation, networking and serialization overhead, future networked worker services, task queues, fault tolerance, cloud deployment.

14. Conclusion
    - Conclusions supported by actual results.

15. References
    - Use a consistent citation style such as IEEE, unless the instructor specifies another format.
    - Cite actual sources consulted; do not invent references.

16. Appendix
    - Selected code, additional tables, or run instructions if needed.

---

## 13. Presentation Outline

Create `reports/presentation_outline.md` for an approximately 5–7 minute presentation with 7–9 slides:

1. Title and team.
2. Problem and motivation.
3. Key CDC concepts.
4. Architecture and coordinator-worker flow.
5. Implementation and tools.
6. Live demo workflow.
7. Actual results and graphs.
8. Limitations and future work.
9. Conclusion and questions.

For every slide, provide:
- Slide title.
- 3–5 concise bullets.
- Suggested visual.
- Short speaker notes in simple English.

Do not claim the system is a real distributed cluster. Explain the current single-machine simulation and the potential extension to networked workers.

---

## 14. Three-Student Work Distribution

### Student 1 — Core processing
- Sequential function.
- Worker function.
- Coordinator and chunk splitting.
- Result aggregation.
- Core correctness tests.

### Student 2 — Experiments and analysis
- Benchmark timing.
- Dataset and worker-count experiments.
- Metrics calculations.
- Results tables and graphs.
- Analysis of overhead.

### Student 3 — Interface and documentation
- Flask dashboard and client-side display.
- Colab notebook presentation support.
- README, report draft, and slides outline.
- Final usability and presentation checks.

All students should review the architecture and results and be ready to answer questions about all components.

---

## 15. Viva Preparation Topics

Prepare simple answers for:
- What is distributed computing?
- How is parallel processing different from distributed computing?
- What is the coordinator's role?
- What is a worker process?
- Why divide a dataset into chunks?
- What is result aggregation?
- Why use multiprocessing for CPU-bound tasks?
- Why can parallel processing be slower for small workloads?
- What is speedup?
- What is parallel efficiency?
- Why must output correctness be validated?
- What is process creation/communication overhead?
- Is this implementation truly multi-machine distributed computing? Why or why not?
- How could it be extended to separate machines?
- What are the limitations of the experiment?

Answers should be understandable to an intermediate undergraduate student.

---

## 16. Final Instructions to the Coding Agent

Build a complete, clean, beginner-readable educational project—not a giant enterprise application.

Priority order:
1. Correct processing engine.
2. Correctness tests.
3. Real benchmark measurements and charts.
4. Working Colab notebook.
5. Simple local Flask dashboard.
6. Accurate report and presentation materials.

Do not:
- Fabricate results.
- Claim multiple machines are used when they are not.
- Add unnecessary databases, authentication, or complex frameworks.
- Hide failed tests.
- leave key files empty or with TODO-only implementations.
- overwrite unrelated files.
- use paid services or require secrets/API keys.

At the end, provide:
- A summary of files created.
- Exact commands to install dependencies and run tests.
- Exact command to start the web app.
- Instructions to open and run the notebook in Google Colab.
- Test results and any known limitations.
- A checklist of what the students must personalize before submission.

Use clear comments and explain important functions so the three students can understand and defend the project in class.
