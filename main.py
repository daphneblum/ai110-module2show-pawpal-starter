from pawpal_system import Owner, Pet, Task, Scheduler, TaskCategory, Priority

# --- Setup: Owner ---
jordan = Owner(
    name="Jordan",
    available_minutes=90,
    preferences="Prioritize medication and feeding before leisure tasks.",
)

# --- Setup: Pets ---
mochi = Pet(name="Mochi", species="dog", age=3)
luna  = Pet(name="Luna",  species="cat", age=5)

# --- Setup: Tasks for Mochi (dog) ---
mochi.add_task(Task(
    id="t1",
    title="Morning walk",
    category=TaskCategory.WALK,
    duration_minutes=30,
    priority=Priority.MEDIUM,
))
mochi.add_task(Task(
    id="t2",
    title="Heartworm medication",
    category=TaskCategory.MEDICATION,
    duration_minutes=5,
    priority=Priority.HIGH,
))

# --- Setup: Tasks for Luna (cat) ---
luna.add_task(Task(
    id="t3",
    title="Breakfast feeding",
    category=TaskCategory.FEEDING,
    duration_minutes=10,
    priority=Priority.HIGH,
))
luna.add_task(Task(
    id="t4",
    title="Brush coat",
    category=TaskCategory.GROOMING,
    duration_minutes=20,
    priority=Priority.LOW,
))
luna.add_task(Task(
    id="t5",
    title="Puzzle feeder enrichment",
    category=TaskCategory.ENRICHMENT,
    duration_minutes=15,
    priority=Priority.LOW,
))

# --- Register pets with owner ---
jordan.add_pet(mochi)
jordan.add_pet(luna)

# --- Generate and print the plan ---
plan = jordan.generate_plan()

print("=" * 45)
print("         PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 45)
print(plan.get_summary())
print()
print("--- Why each task was chosen ---")
scheduler = Scheduler()
print(scheduler.explain_plan(plan))
print("=" * 45)
