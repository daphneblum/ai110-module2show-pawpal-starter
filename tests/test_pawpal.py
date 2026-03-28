import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import date, time, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler, DailyPlan, ScheduledTask, TaskCategory, Priority


# --- Fixtures ---

def make_task(id="t1", title="Walk", duration=20, priority=Priority.MEDIUM):
    return Task(id=id, title=title, category=TaskCategory.WALK,
                duration_minutes=duration, priority=priority)


def make_pet(name="Mochi"):
    return Pet(name=name, species="dog", age=3)


def make_owner(minutes=60):
    return Owner(name="Jordan", available_minutes=minutes, preferences="")


# --- Task tests ---

class TestTask:
    def test_mark_complete(self):
        task = make_task()
        assert task.completed is False
        task.mark_complete()
        assert task.completed is True

    def test_str_shows_priority_and_title(self):
        task = make_task(title="Morning walk", priority=Priority.HIGH)
        result = str(task)
        assert "HIGH" in result
        assert "Morning walk" in result


# --- Pet tests ---

class TestPet:
    def test_add_task(self):
        pet = make_pet()
        task = make_task()
        pet.add_task(task)
        assert task in pet.tasks

    def test_remove_task(self):
        pet = make_pet()
        task = make_task(id="t99")
        pet.add_task(task)
        pet.remove_task("t99")
        assert task not in pet.tasks

    def test_remove_task_nonexistent_does_not_raise(self):
        pet = make_pet()
        pet.remove_task("does-not-exist")  # should not raise

    def test_get_pending_tasks_excludes_completed(self):
        pet = make_pet()
        done = make_task(id="t1")
        done.mark_complete()
        pending = make_task(id="t2", title="Feed")
        pet.add_task(done)
        pet.add_task(pending)
        assert pet.get_pending_tasks() == [pending]


# --- Owner tests ---

class TestOwner:
    def test_add_pet(self):
        owner = make_owner()
        pet = make_pet()
        owner.add_pet(pet)
        assert pet in owner.pets

    def test_generate_plan_returns_daily_plan(self):
        owner = make_owner()
        pet = make_pet()
        pet.add_task(make_task())
        owner.add_pet(pet)
        plan = owner.generate_plan()
        assert isinstance(plan, DailyPlan)

    def test_generate_plan_owner_name_set(self):
        owner = make_owner()
        plan = owner.generate_plan()
        assert plan.owner_name == "Jordan"


# --- Scheduler tests ---

class TestScheduler:
    def test_prioritize_tasks_high_first(self):
        tasks = [
            make_task(id="t1", priority=Priority.LOW),
            make_task(id="t2", priority=Priority.HIGH),
            make_task(id="t3", priority=Priority.MEDIUM),
        ]
        result = Scheduler().prioritize_tasks(tasks)
        assert result[0].priority == Priority.HIGH
        assert result[1].priority == Priority.MEDIUM
        assert result[2].priority == Priority.LOW

    def test_prioritize_tasks_skips_completed(self):
        done = make_task(id="t1")
        done.mark_complete()
        pending = make_task(id="t2", title="Feed")
        result = Scheduler().prioritize_tasks([done, pending])
        assert done not in result
        assert pending in result

    def test_build_plan_respects_time_limit(self):
        pet = make_pet()
        pet.add_task(make_task(id="t1", duration=40, priority=Priority.HIGH))
        pet.add_task(make_task(id="t2", duration=40, priority=Priority.MEDIUM))
        # Only 60 minutes available — second task should not fit
        plan = Scheduler().build_plan([pet], available_minutes=60, owner_name="Jordan")
        assert plan.total_minutes_used <= 60

    def test_build_plan_orders_by_priority(self):
        pet = make_pet()
        pet.add_task(make_task(id="t1", title="Low task",  duration=10, priority=Priority.LOW))
        pet.add_task(make_task(id="t2", title="High task", duration=10, priority=Priority.HIGH))
        plan = Scheduler().build_plan([pet], available_minutes=60, owner_name="Jordan")
        titles = [st.task.title for st in plan.scheduled_tasks]
        assert titles.index("High task") < titles.index("Low task")

    def test_build_plan_includes_pet_name(self):
        pet = make_pet(name="Luna")
        pet.add_task(make_task())
        plan = Scheduler().build_plan([pet], available_minutes=60, owner_name="Jordan")
        assert all(st.pet_name == "Luna" for st in plan.scheduled_tasks)

    def test_build_plan_multiple_pets(self):
        dog = make_pet(name="Mochi")
        cat = make_pet(name="Luna")
        dog.add_task(make_task(id="t1", title="Walk",  duration=20, priority=Priority.HIGH))
        cat.add_task(make_task(id="t2", title="Feed",  duration=10, priority=Priority.HIGH))
        plan = Scheduler().build_plan([dog, cat], available_minutes=60, owner_name="Jordan")
        pet_names = {st.pet_name for st in plan.scheduled_tasks}
        assert "Mochi" in pet_names
        assert "Luna" in pet_names


# --- DailyPlan tests ---

class TestDailyPlan:
    def test_total_minutes_used_reflects_added_tasks(self):
        owner = make_owner(minutes=120)
        pet = make_pet()
        pet.add_task(make_task(id="t1", duration=30))
        pet.add_task(make_task(id="t2", duration=20))
        owner.add_pet(pet)
        plan = owner.generate_plan()
        assert plan.total_minutes_used == 50

    def test_get_summary_contains_owner_name(self):
        owner = make_owner()
        pet = make_pet()
        pet.add_task(make_task())
        owner.add_pet(pet)
        plan = owner.generate_plan()
        assert "Jordan" in plan.get_summary()

    def test_get_summary_empty_plan(self):
        owner = make_owner()
        plan = owner.generate_plan()
        assert "No tasks" in plan.get_summary()


# --- Sorting tests ---

class TestSortByTime:
    def test_timed_tasks_returned_in_chronological_order(self):
        tasks = [
            Task(id="t1", title="Lunch", category=TaskCategory.FEEDING,
                 duration_minutes=10, priority=Priority.MEDIUM, preferred_time="12:00"),
            Task(id="t2", title="Morning walk", category=TaskCategory.WALK,
                 duration_minutes=20, priority=Priority.HIGH, preferred_time="08:00"),
            Task(id="t3", title="Evening meds", category=TaskCategory.MEDICATION,
                 duration_minutes=5, priority=Priority.HIGH, preferred_time="18:30"),
        ]
        result = Scheduler().sort_by_time(tasks)
        assert [t.preferred_time for t in result] == ["08:00", "12:00", "18:30"]

    def test_untimed_tasks_sort_to_end(self):
        tasks = [
            Task(id="t1", title="Grooming", category=TaskCategory.GROOMING,
                 duration_minutes=30, priority=Priority.LOW, preferred_time=""),
            Task(id="t2", title="Walk", category=TaskCategory.WALK,
                 duration_minutes=20, priority=Priority.HIGH, preferred_time="07:00"),
        ]
        result = Scheduler().sort_by_time(tasks)
        assert result[0].preferred_time == "07:00"
        assert result[-1].preferred_time == ""

    def test_original_list_is_not_mutated(self):
        tasks = [
            Task(id="t1", title="Walk", category=TaskCategory.WALK,
                 duration_minutes=20, priority=Priority.HIGH, preferred_time="10:00"),
            Task(id="t2", title="Feed", category=TaskCategory.FEEDING,
                 duration_minutes=10, priority=Priority.MEDIUM, preferred_time="08:00"),
        ]
        original_order = [t.id for t in tasks]
        Scheduler().sort_by_time(tasks)
        assert [t.id for t in tasks] == original_order


# --- Recurrence tests ---

class TestRecurrence:
    def test_completing_daily_task_creates_next_occurrence(self):
        pet = make_pet()
        task = Task(id="t1", title="Morning walk", category=TaskCategory.WALK,
                    duration_minutes=20, priority=Priority.HIGH,
                    recurrence="daily", due_date=date(2026, 3, 28))
        pet.add_task(task)

        next_task = Scheduler().complete_task(task, pet)

        assert next_task is not None
        assert next_task.due_date == date(2026, 3, 29)

    def test_completing_daily_task_increments_id(self):
        pet = make_pet()
        task = Task(id="t1", title="Walk", category=TaskCategory.WALK,
                    duration_minutes=20, priority=Priority.HIGH,
                    recurrence="daily", due_date=date(2026, 3, 28))
        pet.add_task(task)

        next_task = Scheduler().complete_task(task, pet)
        assert next_task.id == "t1_r1"

        # Complete the recurrence — should become t1_r2, not t1_r1_r1
        pet.add_task(next_task)
        second = Scheduler().complete_task(next_task, pet)
        assert second.id == "t1_r2"

    def test_completing_weekly_task_advances_by_seven_days(self):
        pet = make_pet()
        task = Task(id="t2", title="Bath", category=TaskCategory.GROOMING,
                    duration_minutes=45, priority=Priority.MEDIUM,
                    recurrence="weekly", due_date=date(2026, 3, 28))
        pet.add_task(task)

        next_task = Scheduler().complete_task(task, pet)

        assert next_task is not None
        assert next_task.due_date == date(2026, 4, 4)

    def test_completing_one_time_task_returns_none(self):
        pet = make_pet()
        task = Task(id="t3", title="Vet visit", category=TaskCategory.OTHER,
                    duration_minutes=60, priority=Priority.HIGH,
                    recurrence="")
        pet.add_task(task)

        result = Scheduler().complete_task(task, pet)

        assert result is None

    def test_completed_task_is_marked_done(self):
        pet = make_pet()
        task = Task(id="t4", title="Walk", category=TaskCategory.WALK,
                    duration_minutes=20, priority=Priority.MEDIUM,
                    recurrence="daily", due_date=date(2026, 3, 28))
        pet.add_task(task)
        Scheduler().complete_task(task, pet)
        assert task.completed is True

    def test_next_occurrence_added_to_pet(self):
        pet = make_pet()
        task = Task(id="t5", title="Walk", category=TaskCategory.WALK,
                    duration_minutes=20, priority=Priority.HIGH,
                    recurrence="daily", due_date=date(2026, 3, 28))
        pet.add_task(task)
        Scheduler().complete_task(task, pet)
        ids = [t.id for t in pet.tasks]
        assert "t5_r1" in ids


# --- Conflict detection tests ---

class TestDetectConflicts:
    def _make_plan(self, slots: list[tuple[str, str, str, str]]) -> DailyPlan:
        """Helper: slots = [(pet_name, title, 'HH:MM', 'HH:MM'), ...]"""
        plan = DailyPlan(plan_date=date.today(), owner_name="Jordan",
                         total_minutes_available=480)
        for pet_name, title, start_str, end_str in slots:
            task = Task(id=title, title=title, category=TaskCategory.WALK,
                        duration_minutes=0, priority=Priority.MEDIUM)
            sh, sm = (int(x) for x in start_str.split(":"))
            eh, em = (int(x) for x in end_str.split(":"))
            plan.add_scheduled_task(ScheduledTask(
                task=task,
                pet_name=pet_name,
                start_time=time(sh, sm),
                end_time=time(eh, em),
                reason="test",
            ))
        return plan

    def test_overlapping_tasks_flagged(self):
        plan = self._make_plan([
            ("Mochi", "Walk",  "09:00", "09:30"),
            ("Luna",  "Feed",  "09:15", "09:45"),
        ])
        warnings = Scheduler().detect_conflicts(plan)
        assert len(warnings) == 1
        assert "Walk" in warnings[0]
        assert "Feed" in warnings[0]

    def test_back_to_back_tasks_not_flagged(self):
        plan = self._make_plan([
            ("Mochi", "Walk", "09:00", "09:30"),
            ("Luna",  "Feed", "09:30", "10:00"),
        ])
        warnings = Scheduler().detect_conflicts(plan)
        assert warnings == []

    def test_no_tasks_returns_no_warnings(self):
        plan = DailyPlan(plan_date=date.today(), owner_name="Jordan",
                         total_minutes_available=120)
        assert Scheduler().detect_conflicts(plan) == []

    def test_identical_time_window_flagged(self):
        plan = self._make_plan([
            ("Mochi", "Walk", "10:00", "10:30"),
            ("Luna",  "Feed", "10:00", "10:30"),
        ])
        warnings = Scheduler().detect_conflicts(plan)
        assert len(warnings) == 1
