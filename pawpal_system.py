from dataclasses import dataclass, field
from datetime import date
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


@dataclass
class Task:
    id: str
    title: str
    category: TaskCategory
    duration_minutes: int
    priority: Priority
    completed: bool = False
    notes: str = ""


@dataclass
class ScheduledTask:
    task: Task
    start_time: str
    end_time: str
    reason: str


@dataclass
class DailyPlan:
    plan_date: date
    total_minutes_available: int
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    total_minutes_used: int = 0

    def add_scheduled_task(self, st: ScheduledTask) -> None:
        pass

    def get_summary(self) -> str:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_id: str) -> None:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def generate_plan(self) -> DailyPlan:
        pass


class Scheduler:
    def build_plan(self, owner: Owner, pet: Pet) -> DailyPlan:
        pass

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        pass

    def explain_plan(self, plan: DailyPlan) -> str:
        pass
