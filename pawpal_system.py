from dataclasses import dataclass, field
from datetime import date, time, datetime, timedelta
from enum import Enum
from itertools import combinations


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskCategory(Enum):
    WALK = "walk"
    FEEDING = "feeding"
    MEDICATION = "medication"
    GROOMING = "grooming"
    ENRICHMENT = "enrichment"
    OTHER = "other"


# Maps each Priority level to a sort key (lower = scheduled first)
_PRIORITY_ORDER = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}

# Valid recurrence values
_RECURRENCE_DELTA = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


def _next_recurrence_id(task_id: str) -> str:
    """Generate a unique ID for the next recurrence of a task.

    Appends a '_r<n>' suffix on the first recurrence, then increments it on
    each subsequent one so the lineage stays traceable (t1 → t1_r1 → t1_r2).

    Args:
        task_id: The ID of the task being repeated (e.g. "t1" or "t1_r1").

    Returns:
        A new ID string with the recurrence counter incremented by one.
    """
    if "_r" in task_id:
        base, n = task_id.rsplit("_r", 1)
        return f"{base}_r{int(n) + 1}"
    return f"{task_id}_r1"


@dataclass
class Task:
    id: str
    title: str
    category: TaskCategory
    duration_minutes: int
    priority: Priority
    completed: bool = False
    notes: str = ""
    preferred_time: str = ""   # optional "HH:MM" string, e.g. "08:30"
    recurrence: str = ""       # "daily", "weekly", or "" for one-time
    due_date: date | None = None

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> "Task | None":
        """Create a new Task scheduled for the next recurrence date.

        Calculates the next due date by adding the recurrence delta (1 day for
        "daily", 7 days for "weekly") to the task's current due_date, or to
        today if due_date is not set. All other fields are copied from the
        original task so the new instance is identical except for its ID and
        due date.

        Returns:
            A new Task with an incremented ID and updated due_date, or None if
            this task has no recurrence set.
        """
        delta = _RECURRENCE_DELTA.get(self.recurrence)
        if delta is None:
            return None
        base = self.due_date if self.due_date else date.today()
        return Task(
            id=_next_recurrence_id(self.id),
            title=self.title,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            notes=self.notes,
            preferred_time=self.preferred_time,
            recurrence=self.recurrence,
            due_date=base + delta,
        )

    def __str__(self) -> str:
        """Return a human-readable one-line summary of the task."""
        status = "done" if self.completed else "pending"
        return f"[{self.priority.value.upper()}] {self.title} ({self.duration_minutes} min) — {status}"


@dataclass
class ScheduledTask:
    task: Task
    pet_name: str       # which pet this task belongs to
    start_time: time
    end_time: time
    reason: str


@dataclass
class DailyPlan:
    plan_date: date
    owner_name: str             # traceability back to the owner
    total_minutes_available: int
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)

    @property
    def total_minutes_used(self) -> int:
        """Return total scheduled minutes, derived from the task list."""
        return sum(st.task.duration_minutes for st in self.scheduled_tasks)

    def add_scheduled_task(self, st: ScheduledTask) -> None:
        """Append a ScheduledTask to this plan."""
        self.scheduled_tasks.append(st)

    def get_summary(self) -> str:
        """Return a formatted string listing all scheduled tasks and time used."""
        if not self.scheduled_tasks:
            return f"No tasks scheduled for {self.plan_date}."
        lines = [
            f"Daily Plan for {self.owner_name} — {self.plan_date}",
            f"Time used: {self.total_minutes_used} / {self.total_minutes_available} min",
            "",
        ]
        for st in self.scheduled_tasks:
            lines.append(
                f"  {st.start_time.strftime('%H:%M')}–{st.end_time.strftime('%H:%M')} "
                f"[{st.pet_name}] {st.task.title} ({st.task.duration_minutes} min)"
            )
        return "\n".join(lines)


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task by its id; does nothing if the id is not found."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_pending_tasks(self) -> list[Task]:
        """Return all tasks that have not yet been completed."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def generate_plan(self) -> DailyPlan:
        """Entry point: delegates to Scheduler across all owned pets."""
        scheduler = Scheduler()
        return scheduler.build_plan(self.pets, self.available_minutes, self.name)


class Scheduler:
    def build_plan(self, pets: list[Pet], available_minutes: int, owner_name: str) -> DailyPlan:
        """Build a single DailyPlan covering all pets without depending on Owner."""
        plan = DailyPlan(
            plan_date=date.today(),
            owner_name=owner_name,
            total_minutes_available=available_minutes,
        )

        # Collect all pending tasks paired with their pet name
        all_tasks: list[tuple[Task, str]] = [
            (task, pet.name)
            for pet in pets
            for task in pet.get_pending_tasks()
        ]

        # Sort by priority (HIGH first)
        all_tasks.sort(key=lambda pair: _PRIORITY_ORDER[pair[0].priority])

        # Schedule greedily starting at 8:00 AM
        current_dt = datetime(date.today().year, date.today().month, date.today().day, 8, 0)
        minutes_remaining = available_minutes

        for task, pet_name in all_tasks:
            if task.duration_minutes > minutes_remaining:
                continue  # skip tasks that no longer fit

            end_dt = current_dt + timedelta(minutes=task.duration_minutes)
            reason = (
                f"Scheduled because priority is {task.priority.value}; "
                f"fits within remaining time ({minutes_remaining} min left)."
            )
            plan.add_scheduled_task(
                ScheduledTask(
                    task=task,
                    pet_name=pet_name,
                    start_time=current_dt.time(),
                    end_time=end_dt.time(),
                    reason=reason,
                )
            )
            current_dt = end_dt
            minutes_remaining -= task.duration_minutes

        return plan

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted HIGH → MEDIUM → LOW, skipping already-completed ones."""
        pending = [t for t in tasks if not t.completed]
        return sorted(pending, key=lambda t: _PRIORITY_ORDER[t.priority])

    def complete_task(self, task: Task, pet: Pet) -> "Task | None":
        """Mark a task as complete and automatically schedule its next occurrence.

        This is the main entry point for completing a task. It delegates to
        Task.next_occurrence() to create the follow-up task, then registers it
        with the pet so it appears in future plans without manual intervention.

        Args:
            task: The task being completed.
            pet:  The pet this task belongs to; receives the new occurrence if
                  the task is recurring.

        Returns:
            The newly created Task if the task recurs, or None if it is a
            one-time task.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task:
            pet.add_task(next_task)
        return next_task

    def detect_conflicts(self, plan: DailyPlan) -> list[str]:
        """Scan a DailyPlan for scheduling conflicts and return human-readable warnings.

        Uses itertools.combinations to compare every unique pair of scheduled
        tasks exactly once. Two tasks conflict when their time ranges overlap,
        which is true whenever both conditions hold:
            A.start_time < B.end_time  (A begins before B finishes)
            B.start_time < A.end_time  (B begins before A finishes)
        Back-to-back tasks (e.g. 09:00–09:30 followed by 09:30–10:00) are not
        flagged because the boundary values are equal, not strictly less than.

        Args:
            plan: The DailyPlan whose scheduled tasks will be checked.

        Returns:
            A list of warning strings, one per conflicting pair. Returns an
            empty list if the plan has no conflicts.
        """
        warnings = []
        for a, b in combinations(plan.scheduled_tasks, 2):
            if a.start_time < b.end_time and b.start_time < a.end_time:
                    warnings.append(
                        f"WARNING: '{a.task.title}' ({a.pet_name}, "
                        f"{a.start_time.strftime('%H:%M')}–{a.end_time.strftime('%H:%M')}) "
                        f"overlaps with '{b.task.title}' ({b.pet_name}, "
                        f"{b.start_time.strftime('%H:%M')}–{b.end_time.strftime('%H:%M')})"
                    )
        return warnings

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks chronologically by their preferred_time field.

        Converts each "HH:MM" string into an (hour, minute) integer tuple so
        the comparison is numeric rather than lexicographic, avoiding edge cases
        with non-zero-padded values. Tasks whose preferred_time is empty are
        assigned a sentinel value of (24, 0) so they sort to the end of the
        list rather than raising an error.

        Args:
            tasks: The list of Task objects to sort. The original list is not
                   modified.

        Returns:
            A new list of Tasks ordered earliest to latest, with un-timed tasks
            appended at the end.
        """
        return sorted(
            tasks,
            key=lambda t: tuple(int(x) for x in t.preferred_time.split(":")) if t.preferred_time else (24, 0),
        )

    def explain_plan(self, plan: DailyPlan) -> str:
        """Return a human-readable explanation of why each task was scheduled."""
        if not plan.scheduled_tasks:
            return "No tasks were scheduled. Check that pets have pending tasks and the owner has available time."

        lines = [f"Schedule explanation for {plan.owner_name} on {plan.plan_date}:", ""]
        for i, st in enumerate(plan.scheduled_tasks, start=1):
            lines.append(
                f"{i}. {st.task.title} ({st.pet_name})\n"
                f"   Time: {st.start_time.strftime('%H:%M')} – {st.end_time.strftime('%H:%M')}\n"
                f"   Why: {st.reason}"
            )
        skipped_minutes = plan.total_minutes_available - plan.total_minutes_used
        lines.append(f"\n{skipped_minutes} minutes left unscheduled.")
        return "\n".join(lines)
