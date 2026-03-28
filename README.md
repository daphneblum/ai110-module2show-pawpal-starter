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

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
