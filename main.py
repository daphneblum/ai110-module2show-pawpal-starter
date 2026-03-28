from datetime import date, time
from pawpal_system import Owner, Pet, Task, Scheduler, TaskCategory, Priority, DailyPlan, ScheduledTask

# --- Setup: Owner ---
jordan = Owner(
    name="Jordan",
    available_minutes=90,
    preferences="Prioritize medication and feeding before leisure tasks.",
)

# --- Setup: Pets ---
mochi = Pet(name="Mochi", species="dog", age=3)
luna  = Pet(name="Luna",  species="cat", age=5)

# --- Setup: Tasks for Mochi (dog) — added out of time order ---
mochi.add_task(Task(
    id="t1",
    title="Evening walk",
    category=TaskCategory.WALK,
    duration_minutes=30,
    priority=Priority.MEDIUM,
    preferred_time="17:00",
    recurrence="daily",
    due_date=date.today(),
))
mochi.add_task(Task(
    id="t2",
    title="Heartworm medication",
    category=TaskCategory.MEDICATION,
    duration_minutes=5,
    priority=Priority.HIGH,
    preferred_time="08:00",
    recurrence="weekly",
    due_date=date.today(),
))
mochi.add_task(Task(
    id="t3",
    title="Afternoon play",
    category=TaskCategory.ENRICHMENT,
    duration_minutes=20,
    priority=Priority.LOW,
    preferred_time="14:30",
    # no recurrence — one-time task
))

# --- Setup: Tasks for Luna (cat) — added out of time order ---
luna.add_task(Task(
    id="t4",
    title="Puzzle feeder enrichment",
    category=TaskCategory.ENRICHMENT,
    duration_minutes=15,
    priority=Priority.LOW,
    preferred_time="15:00",
    # no recurrence — one-time task
))
luna.add_task(Task(
    id="t5",
    title="Breakfast feeding",
    category=TaskCategory.FEEDING,
    duration_minutes=10,
    priority=Priority.HIGH,
    preferred_time="07:30",
    recurrence="daily",
    due_date=date.today(),
))
luna.add_task(Task(
    id="t6",
    title="Brush coat",
    category=TaskCategory.GROOMING,
    duration_minutes=20,
    priority=Priority.LOW,
    preferred_time="",
    recurrence="weekly",
    due_date=date.today(),
))

# --- Register pets with owner ---
jordan.add_pet(mochi)
jordan.add_pet(luna)

# --- Demo: sort_by_time() across all tasks ---
scheduler = Scheduler()
all_tasks = mochi.tasks + luna.tasks

print("=" * 45)
print("   TASKS AS ADDED (out of order)")
print("=" * 45)
for t in all_tasks:
    time_label = t.preferred_time if t.preferred_time else "(no time)"
    print(f"  {time_label:>10}  [{t.priority.value.upper():^6}]  {t.title}")

print()
print("=" * 45)
print("   SORTED BY TIME (sort_by_time)")
print("=" * 45)
sorted_tasks = scheduler.sort_by_time(all_tasks)
for t in sorted_tasks:
    time_label = t.preferred_time if t.preferred_time else "(no time)"
    print(f"  {time_label:>10}  [{t.priority.value.upper():^6}]  {t.title}")

print()
print("=" * 45)
print("   FILTERED: PENDING ONLY (prioritize_tasks)")
print("=" * 45)
# Mark one task complete to show the filter works
mochi.tasks[2].mark_complete()   # "Afternoon play" is done
pending = scheduler.prioritize_tasks(all_tasks)
for t in pending:
    print(f"  [{t.priority.value.upper():^6}]  {t.title}")

print()
print("=" * 45)
print("   RECURRENCE: complete_task() demo")
print("=" * 45)

# Complete the two daily/weekly tasks and check that next occurrences are created
walk_task = mochi.tasks[0]        # "Evening walk" — daily
feeding_task = luna.tasks[1]      # "Breakfast feeding" — daily
medication_task = mochi.tasks[1]  # "Heartworm medication" — weekly
oneoff_task = mochi.tasks[2]      # "Afternoon play" — no recurrence

for task, pet, label in [
    (walk_task,       mochi, "daily"),
    (medication_task, mochi, "weekly"),
    (feeding_task,    luna,  "daily"),
    (oneoff_task,     mochi, "one-time"),
]:
    before = len(pet.tasks)
    next_t = scheduler.complete_task(task, pet)
    after = len(pet.tasks)
    if next_t:
        print(f"  COMPLETED ({label}): '{task.title}'")
        print(f"    → Next occurrence: '{next_t.title}' (id={next_t.id}, due={next_t.due_date})")
        print(f"    → {pet.name}'s task count: {before} → {after}")
    else:
        print(f"  COMPLETED (one-time): '{task.title}' — no next occurrence created")
        print(f"    → {pet.name}'s task count unchanged: {after}")

print()
print("=" * 45)
print("   CONFLICT DETECTION: detect_conflicts()")
print("=" * 45)

# Manually build a plan with two overlapping tasks to trigger warnings.
# Task A: Mochi's bath — 09:00 to 09:30
# Task B: Luna's feeding — 09:15 to 09:25  (starts inside A's window)
# Task C: Mochi's walk  — 10:00 to 10:30   (no overlap — clean)
conflict_plan = DailyPlan(
    plan_date=date.today(),
    owner_name="Jordan",
    total_minutes_available=120,
)
conflict_plan.add_scheduled_task(ScheduledTask(
    task=Task(id="c1", title="Bath time", category=TaskCategory.GROOMING,
              duration_minutes=30, priority=Priority.MEDIUM),
    pet_name="Mochi",
    start_time=time(9, 0),
    end_time=time(9, 30),
    reason="manual demo",
))
conflict_plan.add_scheduled_task(ScheduledTask(
    task=Task(id="c2", title="Lunch feeding", category=TaskCategory.FEEDING,
              duration_minutes=10, priority=Priority.HIGH),
    pet_name="Luna",
    start_time=time(9, 15),
    end_time=time(9, 25),
    reason="manual demo",
))
conflict_plan.add_scheduled_task(ScheduledTask(
    task=Task(id="c3", title="Afternoon walk", category=TaskCategory.WALK,
              duration_minutes=30, priority=Priority.MEDIUM),
    pet_name="Mochi",
    start_time=time(10, 0),
    end_time=time(10, 30),
    reason="manual demo",
))

conflicts = scheduler.detect_conflicts(conflict_plan)
if conflicts:
    for w in conflicts:
        print(f"  {w}")
else:
    print("  No conflicts detected.")

print()
print("=" * 45)
print("         PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 45)
plan = jordan.generate_plan()
print(plan.get_summary())
print()
print("--- Why each task was chosen ---")
print(scheduler.explain_plan(plan))

print()
print("  Verifying generated plan has no conflicts:")
clean_conflicts = scheduler.detect_conflicts(plan)
if clean_conflicts:
    for w in clean_conflicts:
        print(f"  {w}")
else:
    print("  No conflicts detected.")
print("=" * 45)
