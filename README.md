# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

### Owner & pet profile
Set up an owner with a daily time budget and register one or more pets. Each pet maintains its own independent task list, and all pets are considered together when a plan is generated.

### Task management
Add tasks to any pet with a title, category (walk, feeding, medication, grooming, enrichment, or other), duration in minutes, and priority level. Tasks can be marked complete or removed by ID at any time.

### Priority-based scheduling
When generating a daily plan, PawPal+ sorts all pending tasks across all pets from HIGH to MEDIUM to LOW, then greedily fills the available time budget in that order. Tasks that do not fit within the remaining time are skipped rather than truncated, so every scheduled task runs to completion.

### Time-based sorting
Tasks can be assigned an optional preferred start time (`HH:MM`). `Scheduler.sort_by_time()` orders any list of tasks chronologically by parsing preferred times into numeric hour/minute tuples for accurate comparison. Tasks without a preferred time are placed at the end.

### Recurring tasks
Tasks can be set to repeat `"daily"` or `"weekly"`. When `Scheduler.complete_task()` is called, it marks the task done and automatically registers the next occurrence on the pet's task list with an updated due date and an incremented ID (e.g. `t1 → t1_r1 → t1_r2`). One-time tasks are unaffected.

### Conflict detection
`Scheduler.detect_conflicts()` checks every unique pair of scheduled tasks using the standard interval overlap test. It returns plain-English warning strings rather than raising an exception, so the app stays running and the owner can decide how to resolve each clash. Back-to-back tasks are not flagged.

### Schedule explanation
After a plan is generated, `Scheduler.explain_plan()` produces a human-readable summary of each scheduled task — including its time window, which pet it belongs to, and why it was chosen — so the owner always understands the reasoning behind the plan.

### Multi-pet support
A single owner can register multiple pets. `Scheduler.build_plan()` collects pending tasks across all pets, schedules them within one shared time budget, and labels each scheduled task with the pet's name so the owner knows who each task is for.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Smarter Scheduling

Beyond the core daily planner, `pawpal_system.py` includes several algorithms that make scheduling more useful for real pet owners.

**Time-based sorting** — `Scheduler.sort_by_time()` orders any list of tasks by their `preferred_time` field (stored as an `"HH:MM"` string). Times are parsed into `(hour, minute)` integer tuples for accurate numeric comparison, and tasks without a preferred time are placed at the end.

**Recurring tasks** — Tasks can be marked `"daily"` or `"weekly"`. When `Scheduler.complete_task()` is called, it marks the task done and automatically adds the next occurrence to the pet's task list with an updated due date (`timedelta` of 1 or 7 days) and an incremented ID (e.g. `t1 → t1_r1 → t1_r2`). One-time tasks are unaffected.

**Conflict detection** — `Scheduler.detect_conflicts()` checks every unique pair of scheduled tasks using the standard interval overlap test (`A.start < B.end and B.start < A.end`). It returns a list of plain-English warning strings rather than raising an exception, so the app stays running and the owner can decide how to resolve the clash. Back-to-back tasks are not flagged.

## Testing PawPal+

### Running the tests

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

The suite contains 31 tests across six classes:

| Class | What it verifies |
|---|---|
| `TestTask` | `mark_complete()` flips the flag; `__str__` includes priority and title |
| `TestPet` | Adding, removing, and filtering tasks; missing IDs don't raise |
| `TestOwner` | Pet registration; `generate_plan()` returns a `DailyPlan` with the correct owner name |
| `TestScheduler` | Priority ordering (HIGH → MEDIUM → LOW); time-budget enforcement; multi-pet plans |
| `TestDailyPlan` | `total_minutes_used` sum; `get_summary()` content for populated and empty plans |
| `TestSortByTime` | Chronological ordering of timed tasks; untimed tasks sorted to the end; original list not mutated |
| `TestRecurrence` | Daily/weekly next-occurrence dates; ID chain (`t1 → t1_r1 → t1_r2`); one-time tasks return `None`; new task registered on pet |
| `TestDetectConflicts` | Overlapping windows flagged; back-to-back windows not flagged; identical windows flagged; empty plan returns no warnings |

### Confidence level

**4 / 5 stars**

The core scheduling behaviors — priority ordering, time-budget enforcement, recurrence chains, conflict detection, and time-based sorting — are all exercised with both happy-path and edge-case scenarios, and all 31 tests pass. One star is withheld because the `build_plan` scheduler is greedy (it skips tasks that don't fit without backtracking), which can leave time on the table in ways the current tests don't fully stress-test. Integration-level testing against the Streamlit UI is also not yet covered.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.


### 📸 Demo
<a href=" target=">
<a href="/images/screenshot.png" target="_blank"><img src='/course_images/ai110/your_screenshot_name.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>