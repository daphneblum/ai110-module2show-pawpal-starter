import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, TaskCategory, Priority

PRIORITY_BADGE = {Priority.HIGH: "🔴 High", Priority.MEDIUM: "🟡 Medium", Priority.LOW: "🟢 Low"}

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Owner & Pet setup ---
st.subheader("Owner & Pet")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input("Available minutes today", min_value=10, max_value=480, value=90)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Initialize Owner and Pet in session state only on the first run
if "owner" not in st.session_state:
    st.session_state.pet = Pet(name=pet_name, species=species, age=0)
    st.session_state.owner = Owner(
        name=owner_name,
        available_minutes=int(available_minutes),
        preferences="",
    )
    st.session_state.owner.add_pet(st.session_state.pet)

owner = st.session_state.owner
pet = st.session_state.pet

st.divider()

# --- Add a Task ---
st.subheader("Add a Task")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    priority_map = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}
    new_task = Task(
        id=f"t{len(pet.tasks) + 1}",
        title=task_title,
        category=TaskCategory.OTHER,
        duration_minutes=int(duration),
        priority=priority_map[priority],
    )
    pet.add_task(new_task)       # <- Pet.add_task()
    st.success(f"Added: {new_task}")

if pet.tasks:
    scheduler = Scheduler()
    sorted_tasks = scheduler.prioritize_tasks(pet.tasks)
    st.write(f"**{len(sorted_tasks)} pending task(s) for {pet.name}** — sorted by priority:")
    st.dataframe(
        [
            {
                "Priority": PRIORITY_BADGE[t.priority],
                "Task": t.title,
                "Duration (min)": t.duration_minutes,
            }
            for t in sorted_tasks
        ],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate Schedule ---
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    plan = owner.generate_plan()         # <- Owner.generate_plan()
    scheduler = Scheduler()

    # --- Time summary metrics ---
    st.subheader("Today's Schedule")
    time_used = plan.total_minutes_used
    time_free = plan.total_minutes_available - time_used
    col_used, col_free = st.columns(2)
    col_used.metric("Time Scheduled", f"{time_used} min")
    col_free.metric("Time Remaining", f"{time_free} min")

    # --- Schedule table ---
    if plan.scheduled_tasks:
        st.dataframe(
            [
                {
                    "Time": f"{st.start_time.strftime('%H:%M')}–{st.end_time.strftime('%H:%M')}",
                    "Pet": st.pet_name,
                    "Task": st.task.title,
                    "Duration (min)": st.task.duration_minutes,
                    "Priority": PRIORITY_BADGE[st.task.priority],
                }
                for st in plan.scheduled_tasks
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No tasks could be scheduled. Try adding tasks or increasing available time.")

    # --- Conflict warnings ---
    # Conflicts mean two tasks overlap in time — a pet owner needs to know
    # exactly which tasks clash and what they can do about it, not just that
    # something went wrong. Each conflict is shown as its own st.warning so
    # multiple problems are visually distinct and easy to scan.
    conflicts = scheduler.detect_conflicts(plan)  # <- Scheduler.detect_conflicts()
    if conflicts:
        st.subheader(f"⚠️ {len(conflicts)} Scheduling Conflict(s) Found")
        for conflict in conflicts:
            # Strip the leading "WARNING: " prefix from the raw message
            detail = conflict.removeprefix("WARNING: ")
            st.warning(
                f"**Overlap detected:** {detail}\n\n"
                "**What to do:** Shorten one of these tasks, or stagger their start times.",
                icon="⚠️",
            )
    else:
        st.success("No conflicts — your schedule looks good!", icon="✅")

    # --- Explanation ---
    st.divider()
    st.subheader("Why each task was chosen")
    st.text(scheduler.explain_plan(plan))  # <- Scheduler.explain_plan()
