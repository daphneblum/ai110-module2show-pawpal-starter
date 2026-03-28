from dataclasses import dataclass, field
from datetime import date, time, datetime, timedelta
from enum import Enum


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


@dataclass
class Task:
    id: str
    title: str
    category: TaskCategory
    duration_minutes: int
    priority: Priority
    completed: bool = False
    notes: str = ""

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

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
