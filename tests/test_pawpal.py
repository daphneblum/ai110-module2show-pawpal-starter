import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pawpal_system import Owner, Pet, Task, Scheduler, DailyPlan, TaskCategory, Priority


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
